from django.contrib import admin
from django.utils.html import format_html # Images aur Colors ke liye
from .models import (
    Category, Product, Slider, GiftCard, 
    CartItem, Wishlist, ShippingAddress, Order
)

# 1. Basic Models
admin.site.register(Category)
admin.site.register(Slider)
admin.site.register(GiftCard)
admin.site.register(CartItem)
admin.site.register(Wishlist)
admin.site.register(ShippingAddress)

# 2. Advanced Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # 'thumbnail' function niche define kiya hai photo dikhane ke liye
    list_display = ('thumbnail', 'name', 'category', 'price', 'stock', 'available')
    list_filter = ('category', 'available', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'available')
    list_per_page = 20

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height:45px; border-radius: 5px;" />', obj.image.url)
        return "No Image"
    thumbnail.short_description = 'Photo'

# 3. Pro Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'customer_info', # Naam aur Number ek saath
        'amount_display', 
        'status_colored', # Color coded status
        'is_paid', 
        'payment_method',
        'created_at'
    )
    
    list_filter = ('status', 'is_paid', 'payment_method', 'created_at')
    search_fields = ('id', 'full_name', 'phone', 'user__username')
    list_editable = ('status', 'is_paid')
    ordering = ('-created_at',)
    list_per_page = 15

    # Customer ka naam aur phone ek hi column mein professional lagta hai
    def customer_info(self, obj):
        return format_html('<b>{}</b><br><small class="text-muted">{}</small>', obj.full_name, obj.phone)
    customer_info.short_description = 'Customer Details'

    # Amount ko Rupee symbol ke saath dikhane ke liye
    def amount_display(self, obj):
        return f"₹{obj.amount}"
    amount_display.short_description = 'Total Amount'

    # Status ke hisaab se color badges
    def status_colored(self, obj):
        colors = {
            'Pending': '#ff9800', # Orange
            'Packed': '#2196f3',  # Blue
            'Shipped': '#9c27b0', # Purple
            'Delivered': '#4caf50', # Green
            'Cancelled': '#f44336', # Red
        }
        color = colors.get(obj.status, '#000')
        return format_html('<b style="color: {};">{}</b>', color, obj.status)
    status_colored.short_description = 'Current Status'

    # Bulk actions: Ek saath sabko paid mark karna
    actions = ['mark_as_paid']

    def mark_as_paid(self, request, queryset):
        queryset.update(is_paid=True)
    mark_as_paid.short_description = "Mark selected orders as Paid"

# Header aur Title change karein (Admin Panel ka look badalne ke liye)
admin.site.site_header = "Apna Mart Admin"
admin.site.site_title = "Apna Mart Portal"
admin.site.index_title = "Welcome to Shop Management"