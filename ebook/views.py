import uuid
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

# Models import
from .models import Product, Category, CartItem, Order, OrderItem, Wishlist, Slider

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_wishlist_count(request):
    if request.user.is_authenticated:
        return Wishlist.objects.filter(user=request.user).count()
    return 0

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
    
    products = Product.objects.filter(available=True).select_related('category')
    
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
        'wishlist_ids': list(wishlist_ids), 
        'selected_category': category_name, 
        'query': query,
        'wishlist_count': get_wishlist_count(request)
    })

def all_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(available=True)
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    
    return render(request, 'ebook/all_products.html', {
        'products': products.order_by('-id'), 
        'query': query,
        'wishlist_count': get_wishlist_count(request)
    })

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'ebook/details.html', {
        'product': product,
        'wishlist_count': get_wishlist_count(request)
    })

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, available=True).order_by('-id')
    sliders = Slider.objects.all() 
    categories = Category.objects.all()

    return render(request, 'ebook/index.html', {
        'products': products, 
        'categories': categories, 
        'sliders': sliders, 
        'selected_category': category.name,
        'wishlist_count': get_wishlist_count(request)
    })

def search_view(request):
    return product_list(request)

def offer_zone(request):
    products = Product.objects.filter(available=True, old_price__isnull=False).order_by('-id')[:12]
    return render(request, 'ebook/offer_zone.html', {
        'products': products,
        'wishlist_count': get_wishlist_count(request)
    })

# ==========================================
# 2. CART & WISHLIST VIEWS
# ==========================================

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    delivery = 0 if total > 500 or total == 0 else 40
    return render(request, 'ebook/cart.html', {
        'cart_items': cart_items, 
        'total': total, 
        'delivery_charge': delivery, 
        'grand_total': total + delivery,
        'wishlist_count': get_wishlist_count(request)
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.stock < 1:
        messages.error(request, "Out of Stock!")
        return redirect('product_list')
    item, created = CartItem.objects.get_or_create(product=product, user=request.user)
    if not created: 
        item.quantity += 1
        item.save()
    messages.success(request, "Added to cart!")
    return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    get_object_or_404(CartItem, id=item_id, user=request.user).delete()
    messages.success(request, "Item removed.")
    return redirect('view_cart')

@csrf_exempt
@login_required
def update_item(request):
    data = json.loads(request.body)
    product_id = data.get('productId')
    action = data.get('action')
    product = get_object_or_404(Product, id=product_id)
    cart_item, _ = CartItem.objects.get_or_create(user=request.user, product=product)

    if action == 'add' and product.stock > cart_item.quantity:
        cart_item.quantity += 1
    elif action == 'remove':
        cart_item.quantity -= 1
    
    cart_item.save()
    if cart_item.quantity <= 0: cart_item.delete()
    return JsonResponse({'status': 'success'})

@login_required
def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if item.product.stock > item.quantity:
        item.quantity += 1
        item.save()
    return redirect('view_cart')

@login_required
def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
    return redirect('view_cart')

@login_required
def view_wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'ebook/wishlist.html', {'wishlist_items': items, 'wishlist_count': get_wishlist_count(request)})

@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    w, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created: 
        w.delete()
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

# ==========================================
# 3. CHECKOUT & ORDERS (FIXED)
# ==========================================

@login_required
def checkout(request, product_id=None):
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        cart_items = [{'product': product, 'quantity': 1, 'total_price_val': product.price, 'id': None}]
        total = product.price
        single_product_id = product_id
    else:
        cart_qs = CartItem.objects.filter(user=request.user)
        if not cart_qs.exists(): return redirect('product_list')
        cart_items = [{'product': i.product, 'quantity': i.quantity, 'total_price_val': i.total_price(), 'id': i.id} for i in cart_qs]
        total = sum(i['total_price_val'] for i in cart_items)
        single_product_id = None

    delivery = 0 if total > 500 else 40
    return render(request, 'ebook/checkout.html', {
        'cart_items': cart_items, 'total': total, 'delivery_charge': delivery, 
        'grand_total': total + delivery, 'single_product_id': single_product_id,
        'wishlist_count': get_wishlist_count(request), 'upi_id': 'krishugodle@oksbi'
    })

@login_required
def place_order(request):
    if request.method == "POST":
        single_prod_id = request.POST.get('single_product_id')
        payment_method = request.POST.get('payment_method')
        txn_id = request.POST.get('transaction_id')
        
        # Combine address details
        full_address = f"{request.POST.get('address')}, {request.POST.get('city')}, {request.POST.get('state')} - {request.POST.get('pincode')}"

        with transaction.atomic():
            # Item setup
            if single_prod_id and single_prod_id != "None":
                product = get_object_or_404(Product, id=single_prod_id)
                items = [{'product': product, 'quantity': 1, 'price': product.price}]
            else:
                cart_qs = CartItem.objects.filter(user=request.user)
                if not cart_qs.exists():
                    messages.error(request, "Aapka cart khali hai!")
                    return redirect('product_list')
                items = [{'product': i.product, 'quantity': i.quantity, 'price': i.product.price} for i in cart_qs]

            total_price = sum(i['price'] * i['quantity'] for i in items)
            delivery_charge = 0 if total_price > 500 else 40
            grand_total = total_price + delivery_charge

            # PAYMENT LOGIC MERGED
            # Status management
            if payment_method == 'UPI':
                if not txn_id:
                    messages.error(request, "Kripya Transaction ID enter karein!")
                    return redirect('checkout')
                status = 'Payment Verifying'
                msg = "Order place ho gaya! Payment verify hone ke baad confirm hoga."
            else:
                status = 'Pending'
                msg = "Order successfully place ho gaya!"

            # Order creation
            order = Order.objects.create(
                user=request.user, 
                order_id=f"ORD{uuid.uuid4().hex[:8].upper()}",
                amount=grand_total, 
                payment_method=payment_method,
                full_name=request.POST.get('full_name'), 
                phone=request.POST.get('phone'),
                address=full_address,
                status=status, 
                transaction_id=txn_id if txn_id else f"COD-{uuid.uuid4().hex[:6].upper()}"
            )

            # Save items and update stock
            for i in items:
                OrderItem.objects.create(
                    order=order, product=i['product'], price=i['price'], quantity=i['quantity']
                )
                i['product'].stock -= i['quantity']
                i['product'].save()

            if not single_prod_id or single_prod_id == "None":
                CartItem.objects.filter(user=request.user).delete()

            messages.success(request, msg)
            return redirect('order_success', order_id=order.order_id)
            
    return redirect('checkout')

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, 'ebook/my_orders.html', {'orders': orders, 'wishlist_count': get_wishlist_count(request)})

def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, 'ebook/success.html', {'order': order})

@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'ebook/track_order.html', {'order': order})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    if order.status in ['Pending', 'Payment Verifying']:
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save()
        order.status = 'Cancelled'
        order.save()
        messages.info(request, "Order cancel kar diya gaya hai.")
    return redirect('my_orders')

# ==========================================
# 4. AUTH VIEWS
# ==========================================

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    return render(request, 'ebook/signup.html', {'form': UserCreationForm()})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('product_list')
    return render(request, 'ebook/login.html', {'form': AuthenticationForm()})

def logout_view(request):
    logout(request)
    return redirect('product_list')