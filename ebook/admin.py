from django.contrib import admin
from .models import (
    Category, Product, Slider, GiftCard, 
    CartItem, Wishlist, ShippingAddress, Order
)

# 1. Simple Models Registration
admin.site.register(Category)
admin.site.register(Slider)
admin.site.register(GiftCard)
admin.site.register(CartItem)
admin.site.register(Wishlist)
admin.site.register(ShippingAddress)

# 2. Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'available')
    list_filter = ('category', 'available')
    search_fields = ('name',)

# 3. Order Admin (Tracking System ke liye sabse important)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Ye columns aapko admin table mein dikhenge
    list_display = ('order_id', 'user', 'amount', 'status', 'is_paid', 'created_at')
    
    # Filter aur Search functionality
    list_filter = ('status', 'is_paid', 'payment_method')
    search_fields = ('order_id', 'user__username')
    
    # Isse aap admin page ke bahar se hi status update kar sakte hain
    list_editable = ('status', 'is_paid')