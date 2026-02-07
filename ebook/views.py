import uuid
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, CartItem, Order, Wishlist, GiftCard, Slider 
from django.db.models import Q 
from django.views.decorators.csrf import csrf_exempt

# ==========================================
# 1. PRODUCT & SHOP VIEWS
# ==========================================
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
        'wishlist_ids': wishlist_ids,
        'selected_category': category_name,
        'query': query
    })

def all_products(request):
    products = Product.objects.filter(available=True).order_by('-id')
    return render(request, 'ebook/all_products.html', {'products': products})

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'ebook/details.html', {'product': product})

def offer_zone(request):
    products = Product.objects.filter(available=True).order_by('-id')[:12]
    return render(request, 'ebook/offer_zone.html', {'products': products})

# ==========================================
# 2. AUTHENTICATION VIEWS
# ==========================================
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please Login.")
            return redirect('login')
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
    messages.success(request, "Logged out successfully.")
    return redirect('product_list') 

# ==========================================
# 3. CART & WISHLIST
# ==========================================
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(product=product, user=request.user)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, "Product added to cart!")
    return redirect('view_cart')

@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    CartItem.objects.get_or_create(product=product, user=request.user)
    return redirect('checkout')

@csrf_exempt
@login_required
def update_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            productId = data['productId']
            action = data['action']
            product = Product.objects.get(id=productId)
            cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
            if action == 'add':
                cart_item.quantity += 1
            elif action == 'remove':
                cart_item.quantity -= 1
            cart_item.save()
            if cart_item.quantity <= 0:
                cart_item.delete()
                return JsonResponse({'status': 'deleted'}, safe=False)
            return JsonResponse({'status': 'updated', 'qty': cart_item.quantity}, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    delivery_charge = 0 if total > 500 or total == 0 else 40
    grand_total = total + delivery_charge
    return render(request, 'ebook/cart.html', {
        'cart_items': cart_items, 
        'total': total, 
        'delivery_charge': delivery_charge,
        'grand_total': grand_total
    })

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

# ==========================================
# 4. CHECKOUT & ORDERS
# ==========================================
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

    delivery_charge = 0 if total > 500 else 40
    grand_total = max(0, total + delivery_charge - discount)
    
    return render(request, 'ebook/checkout.html', {
        'cart_items': cart_items, 
        'total': total,
        'discount': discount,
        'delivery_charge': delivery_charge,
        'grand_total': grand_total,
    })

@login_required
def place_order(request):
    if request.method == "POST":
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items: return redirect('product_list')

        total_price = sum(item.total_price() for item in cart_items)
        discount = 0
        gift_card_id = request.session.get('gift_card_id')
        if gift_card_id:
            gift_card = GiftCard.objects.filter(id=gift_card_id, is_active=True).first()
            if gift_card:
                discount = gift_card.amount
                gift_card.is_active = False
                gift_card.used_by = request.user
                gift_card.save()

        delivery_charge = 0 if total_price > 500 else 40
        final_amount = max(0, total_price + delivery_charge - discount)
        order_id = f"ORD{uuid.uuid4().hex[:8].upper()}"
        payment_mode = request.POST.get('payment_method', 'COD')

        Order.objects.create(
            user=request.user, 
            order_id=order_id, 
            amount=final_amount, 
            payment_method=payment_mode,
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            address=f"{request.POST.get('address')}, {request.POST.get('city')} - {request.POST.get('pincode')}"
        )
        
        cart_items.delete()
        if 'gift_card_id' in request.session: del request.session['gift_card_id']
        
        return render(request, 'ebook/success.html', {'id': order_id, 'amount': final_amount, 'method': payment_mode})
    return redirect('checkout')

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
    if order.status == 'Pending':
        order.status = 'Cancelled'
        order.save()
        messages.success(request, f"Order {order_id} cancelled.")
    else:
        messages.error(request, "Cannot cancel this order.")
    return redirect('my_orders')

# ==========================================
# 5. GIFT CARDS
# ==========================================
def apply_gift_card(request):
    if request.method == "POST":
        code = request.POST.get('code')
        gift_card = GiftCard.objects.filter(code=code, is_active=True).first()
        if gift_card:
            request.session['gift_card_id'] = gift_card.id
            messages.success(request, f"Gift Card Applied! ₹{gift_card.amount} discount.")
        else:
            messages.error(request, "Invalid or Expired Gift Card.")
    return redirect('checkout')

def gift_card_list(request):
    return render(request, 'ebook/gift_cards.html')