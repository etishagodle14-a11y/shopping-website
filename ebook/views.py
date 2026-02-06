import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, CartItem, Order, Wishlist, GiftCard, Slider 
from django.db.models import Q 

# 1. PRODUCT & SHOP VIEWS
def product_list(request):
    query = request.GET.get('q', '').strip()
    category_name = request.GET.get('category')
    categories = Category.objects.all()
    sliders = Slider.objects.all() 
    
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    
    products = Product.objects.filter(available=True)

    if query:
        products = products.filter(
            Q(category__name__icontains=query) | 
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        ).distinct()
    elif category_name and category_name != "All Products":
        products = products.filter(category__name=category_name)
    
    return render(request, 'ebook/index.html', {
        'products': products.order_by('-id'), 
        'categories': categories,
        'sliders': sliders,
        'wishlist_ids': wishlist_ids
    })

def all_products(request):
    products = Product.objects.filter(available=True).order_by('-id')
    return render(request, 'ebook/all_products.html', {'products': products})

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'ebook/details.html', {'product': product})

# 2. AUTHENTICATION VIEWS
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'ebook/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next', 'product_list'))
    else:
        form = AuthenticationForm()
    return render(request, 'ebook/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('product_list')

# 3. CART & WISHLIST
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.info(request, "Please login first.")
        return redirect('login')
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(product=product, user=request.user)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')

def view_cart(request):
    if not request.user.is_authenticated:
        return redirect('login')
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'ebook/cart.html', {'cart_items': cart_items, 'total': total, 'grand_total': total})

def remove_from_cart(request, item_id):
    get_object_or_404(CartItem, id=item_id, user=request.user).delete()
    return redirect('view_cart')

@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        wishlist_item.delete()
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

@login_required
def view_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'ebook/wishlist.html', {'wishlist_items': wishlist_items})

# 4. CHECKOUT & BUY NOW
@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Important: Mobile users ke liye session clear karke fresh cart item create karna
    CartItem.objects.filter(user=request.user).delete()
    CartItem.objects.create(user=request.user, product=product, quantity=1)
    return redirect('checkout')

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        messages.warning(request, "Aapka cart khali hai!")
        return redirect('product_list')
    
    total = sum(item.total_price() for item in cart_items)
    discount = 0
    gift_card_id = request.session.get('gift_card_id')
    if gift_card_id:
        gift_card = GiftCard.objects.filter(id=gift_card_id, is_active=True).first()
        if gift_card:
            discount = gift_card.amount

    grand_total = max(0, total - discount)
    return render(request, 'ebook/checkout.html', {
        'cart_items': cart_items, 
        'total': total,
        'discount': discount,
        'grand_total': grand_total,
    })

@login_required
def place_order(request):
    if request.method == "POST":
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items:
            return redirect('product_list')

        total_price = sum(item.total_price() for item in cart_items)
        # Gift Card Logic Apply
        gift_card_id = request.session.get('gift_card_id')
        discount = 0
        if gift_card_id:
            gift_card = GiftCard.objects.filter(id=gift_card_id, is_active=True).first()
            if gift_card:
                discount = gift_card.amount
                gift_card.is_active = False
                gift_card.used_by = request.user
                gift_card.save()

        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        Order.objects.create(
            user=request.user, 
            order_id=order_id, 
            amount=max(0, total_price - discount), 
            payment_method=request.POST.get('payment_method', 'COD'),
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            address=f"{request.POST.get('address')}, {request.POST.get('city')} - {request.POST.get('pincode')}"
        )
        
        cart_items.delete()
        if 'gift_card_id' in request.session:
            del request.session['gift_card_id']
        
        return render(request, 'ebook/success.html', {'id': order_id})
    return redirect('checkout')

# 5. ORDER TRACKING & EXTRAS
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-id') 
    return render(request, 'ebook/my_orders.html', {'orders': orders})

@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'ebook/track_order.html', {'order': order})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    if order.status not in ['Delivered', 'Cancelled']:
        order.status = 'Cancelled'
        order.save()
    return redirect('my_orders')

def offer_zone(request):
    products = Product.objects.filter(available=True).order_by('-id')[:12]
    return render(request, 'ebook/offer_zone.html', {'products': products})

def gift_card_list(request):
    gift_cards = GiftCard.objects.filter(is_active=True, used_by__isnull=True)
    return render(request, 'ebook/gift_cards.html', {'gift_cards': gift_cards})

@login_required
def apply_gift_card(request):
    if request.method == "POST":
        code = request.POST.get('gift_card_code') 
        gift_card = GiftCard.objects.filter(code=code, is_active=True, used_by__isnull=True).first()
        if gift_card:
            request.session['gift_card_id'] = gift_card.id
            messages.success(request, "Gift Card Applied!")
        else:
            messages.error(request, "Invalid or Expired Gift Card.")
    return redirect('checkout')