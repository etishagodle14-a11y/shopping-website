import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, CartItem, Order, Wishlist, GiftCard, Slider 
from django.db.models import Q 

# ==========================================
# 1. PRODUCT & SHOP VIEWS
# ==========================================

def product_list(request):
    query = request.GET.get('q') 
    category_name = request.GET.get('category')
    categories = Category.objects.all()
    sliders = Slider.objects.all() 
    
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    
    products = Product.objects.filter(available=True)

    if query:
        search_term = query.strip()
        products = products.filter(
            Q(category__name__icontains=search_term) | 
            Q(name__icontains=search_term) | 
            Q(description__icontains=search_term)
        ).distinct()
    
    elif category_name and category_name != "All Products":
        products = products.filter(category__name=category_name)
    
    products = products.order_by('-id')

    return render(request, 'ebook/index.html', {
        'products': products, 
        'categories': categories,
        'selected_category': category_name,
        'query': query,
        'wishlist_ids': wishlist_ids,
        'sliders': sliders 
    })

def all_products(request):
    products = Product.objects.filter(available=True).order_by('-id')
    return render(request, 'ebook/all_products.html', {'products': products})

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'ebook/details.html', {'product': product})

def gift_card_list(request):
    gift_cards = GiftCard.objects.filter(is_active=True, used_by__isnull=True)
    return render(request, 'ebook/gift_cards.html', {'gift_cards': gift_cards})

def offer_zone(request):
    products = Product.objects.filter(available=True).order_by('-id')[:12]
    return render(request, 'ebook/offer_zone.html', {'products': products})

# ==========================================
# 2. AUTHENTICATION VIEWS
# ==========================================

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'ebook/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('product_list')

# ==========================================
# 3. CART & WISHLIST MANAGEMENT
# ==========================================

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user if request.user.is_authenticated else None
    cart_item, created = CartItem.objects.get_or_create(product=product, user=user)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')

def view_cart(request):
    user = request.user if request.user.is_authenticated else None
    cart_items = CartItem.objects.filter(user=user)
    total = sum(item.total_price() for item in cart_items)
    delivery_charge = 0 
    grand_total = total + delivery_charge
    return render(request, 'ebook/cart.html', locals())

def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    messages.success(request, "Item removed.")
    referer = request.META.get('HTTP_REFERER')
    if referer and 'checkout' in referer:
        return redirect('checkout')
    return redirect('view_cart')

@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        wishlist_item.delete()
        messages.info(request, f"{product.name} removed from wishlist.")
    else:
        messages.success(request, f"{product.name} added to wishlist.")
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

@login_required
def view_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'ebook/wishlist.html', {'wishlist_items': wishlist_items})

# ==========================================
# 4. CHECKOUT & ORDER PLACEMENT
# ==========================================

@login_required
def apply_gift_card(request):
    if request.method == "POST":
        code = request.POST.get('gift_card_code') 
        try:
            gift_card = GiftCard.objects.get(code=code, is_active=True, used_by__isnull=True)
            request.session['gift_card_id'] = gift_card.id
            messages.success(request, f"₹{gift_card.amount} Gift Card applied successfully!")
        except GiftCard.DoesNotExist:
            messages.error(request, "Invalid or Expired Gift Card code.")
    return redirect(request.META.get('HTTP_REFERER', 'checkout'))

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        messages.warning(request, "Aapka cart khali hai!")
        return redirect('product_list')
    
    total = sum(item.total_price() for item in cart_items)
    gift_card_id = request.session.get('gift_card_id')
    discount = 0
    if gift_card_id:
        gift_card = GiftCard.objects.filter(id=gift_card_id, is_active=True).first()
        if gift_card:
            discount = gift_card.amount

    delivery_charge = 0 
    grand_total = max(0, (total + delivery_charge) - discount)
    
    return render(request, 'ebook/checkout.html', {
        'cart_items': cart_items, 
        'total': total,
        'delivery_charge': delivery_charge,
        'discount': discount,
        'grand_total': grand_total,
    })

@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    CartItem.objects.filter(user=request.user).delete()
    CartItem.objects.create(user=request.user, product=product, quantity=1)
    return redirect('checkout')

@login_required
def place_order(request):
    if request.method == "POST":
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items: 
            return redirect('product_list')

        # Form Data Fetch
        raw_payment = request.POST.get('payment_method') 
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address_text = request.POST.get('address')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        state = request.POST.get('state', '')

        if not raw_payment:
            messages.error(request, "Please select a payment method.")
            return redirect('checkout')

        # Logic Fix: template se 'UPI' ya 'COD' aayega
        payment_mode = 'UPI' if raw_payment == 'UPI' else 'COD'

        # Calculation
        total_price = sum(item.total_price() for item in cart_items)
        gift_card_id = request.session.get('gift_card_id')
        discount = 0
        
        if gift_card_id:
            gift_card = GiftCard.objects.filter(id=gift_card_id, is_active=True).first()
            if gift_card:
                discount = gift_card.amount
                gift_card.is_active = False
                gift_card.used_by = request.user
                gift_card.save()

        grand_total = max(0, total_price - discount)
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Save Order
        Order.objects.create(
            user=request.user, 
            order_id=order_id, 
            amount=grand_total, 
            payment_method=payment_mode,
            full_name=full_name,
            phone=phone,
            address=f"{address_text}, {city}, {state} - {pincode}"
        )
        
        # Cleanup
        if 'gift_card_id' in request.session:
            del request.session['gift_card_id']
            
        cart_items.delete()
        messages.success(request, "Order placed successfully!")
        
        # FIX: Pass 'method' to success page
        return render(request, 'ebook/success.html', {
            'id': order_id, 
            'method': payment_mode  # Ab ye "UPI" ya "COD" template ko milega
        })
        
    return redirect('checkout')

# ==========================================
# 5. ORDER TRACKING & MANAGEMENT
# ==========================================

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
    if order.status != 'Delivered' and order.status != 'Cancelled':
        order.status = 'Cancelled'
        order.save()
        messages.success(request, f"Order #{order_id} has been cancelled.")
    else:
        messages.error(request, "This order cannot be cancelled.")
    return redirect('my_orders')