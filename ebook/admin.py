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

# 2. Product Admin (Isse products manage karna asaan hoga)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'available')
    list_filter = ('category', 'available')
    search_fields = ('name',)

# 3. Merged Order Admin (Customer details aur Tracking ke liye)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Ye columns aapko admin ki main list mein dikhenge
    list_display = (
        'id', 
        'full_name',   # Customer ka naam
        'phone',       # Mobile number
        'amount',      # Kitne ka order hai
        'status',      # Pending/Completed
        'is_paid',     # Paise mile ya nahi
        'created_at'   # Order kab aaya
    )
    
    # Side mein filter karne ke liye options
    list_filter = ('status', 'is_paid', 'payment_method', 'created_at')
    
    # Search box mein kya-kya dhund sakte hain
    search_fields = ('id', 'full_name', 'phone', 'user__username')
    
    # Seedhe table se status change karne ke liye
    list_editable = ('status', 'is_paid')
    
    # Taaki latest order sabse upar dikhe
    ordering = ('-created_at',)