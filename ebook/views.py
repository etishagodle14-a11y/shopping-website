from django.db import transaction # Taaki order aur items ek saath save hon
from .models import Product, Category, CartItem, Order, OrderItem, Wishlist, GiftCard, Slider 

# --- PRODUCT & SHOP (Optimized) ---
def product_list(request):
    query = request.GET.get('q', '').strip()
    category_name = request.GET.get('category')
    
    # Prefetching taaki database par load kam pade
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
        'wishlist_ids': wishlist_ids,
        'selected_category': category_name,
        'query': query
    })

# --- UPDATED PLACE ORDER (With Item Storage) ---
@login_required
def place_order(request):
    if request.method == "POST":
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items:
            messages.error(request, "Your cart is empty!")
            return redirect('product_list')

        # Use transaction.atomic taaki agar ek bhi step fail ho, toh poora data roll-back ho jaye
        with transaction.atomic():
            total_price = sum(item.total_price() for item in cart_items)
            discount = 0
            
            # Gift Card Logic
            gift_card_id = request.session.get('gift_card_id')
            if gift_card_id:
                gift_card = GiftCard.objects.select_for_update().filter(id=gift_card_id, is_active=True).first()
                if gift_card:
                    discount = gift_card.amount
                    gift_card.is_active = False
                    gift_card.used_by = request.user
                    gift_card.save()

            delivery_charge = 0 if total_price > 500 else 40
            final_amount = max(0, total_price + delivery_charge - discount)
            order_id = f"ORD{uuid.uuid4().hex[:8].upper()}"
            
            # 1. Create Main Order
            order = Order.objects.create(
                user=request.user, 
                order_id=order_id, 
                amount=final_amount, 
                payment_method=request.POST.get('payment_method', 'COD'),
                full_name=request.POST.get('full_name'),
                phone=request.POST.get('phone'),
                address=f"{request.POST.get('address')}, {request.POST.get('city')} - {request.POST.get('pincode')}"
            )

            # 2. Save Order Items (PEHLE YEH MISSING THA)
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price, # Purchase time ka price lock kar rahe hain
                    quantity=item.quantity
                )
                # Stock update karna mat bhulna!
                item.product.stock -= item.quantity
                item.product.save()

            # 3. Clear Cart & Session
            cart_items.delete()
            if 'gift_card_id' in request.session: 
                del request.session['gift_card_id']
        
        return render(request, 'ebook/success.html', {
            'id': order_id, 
            'amount': final_amount, 
            'method': order.payment_method
        })
        
    return redirect('checkout')