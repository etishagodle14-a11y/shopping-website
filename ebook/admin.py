from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from django.core.cache import cache

# Apne models import karein
from .models import Product, Category, CartItem, Order, OrderItem, Wishlist, Slider

# ==========================================
# 1. CUSTOM USER ADMIN (With Live Status)
# ==========================================
admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Live Online Status Check
    def is_online(self, obj):
        last_seen = cache.get(f'seen_{obj.id}')
        if last_seen and (timezone.now() - last_seen).seconds < 300:
            return format_html('<b style="color:green;">● Online</b>')
        return format_html('<b style="color:red;">○ Offline</b>')
    
    is_online.short_description = 'Live Status'

    # Admin list mein columns set karein
    list_display = ('username', 'email', 'is_staff', 'is_online', 'last_login')
    ordering = ('-last_login',)

# ==========================================
# 2. BASIC MODELS REGISTRATION
# ==========================================
admin.site.register(Slider)
admin.site.register(CartItem)
admin.site.register(Wishlist)

# ==========================================
# 3. CATEGORY ADMIN
# ==========================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

# ==========================================
# 4. ADVANCED PRODUCT ADMIN
# ==========================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height:45px; border-radius: 5px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    thumbnail.short_description = 'Photo'

    list_display = ('thumbnail', 'name', 'category', 'price', 'stock', 'available')
    list_filter = ('category', 'available', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'available')
    list_per_page = 20

# ==========================================
# 5. PRO ORDER ADMIN (With Order Items Inline)
# ==========================================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    
    list_display = (
        'order_id', 
        'customer_info', 
        'amount_display', 
        'status_colored', 
        'is_paid', 
        'payment_method',
        'created_at'
    )
    
    list_editable = ('is_paid',) 
    list_filter = ('status', 'is_paid', 'payment_method', 'created_at')
    search_fields = ('order_id', 'full_name', 'phone', 'user__username')
    ordering = ('-created_at',)
    list_per_page = 15

    def customer_info(self, obj):
        return format_html('<b>{}</b><br><small>{}</small>', obj.full_name, obj.phone)
    customer_info.short_description = 'Customer'

    def amount_display(self, obj):
        return format_html('<span style="font-weight: bold;">₹{}</span>', obj.amount)
    amount_display.short_description = 'Total Amount'

    def status_colored(self, obj):
        colors = {
            'Pending': '#ff9800', 
            'Packed': '#2196f3',
            'Shipped': '#9c27b0',
            'Delivered': '#4caf50',
            'Cancelled': '#f44336',
        }
        color = colors.get(obj.status, '#000')
        return format_html('<span style="color: {}; font-weight: bold;">● {}</span>', color, obj.status)
    status_colored.short_description = 'Status'

    actions = ['mark_as_paid']
    def mark_as_paid(self, request, queryset):
        queryset.update(is_paid=True)
        self.message_user(request, "Selected orders marked as Paid.")
    mark_as_paid.short_description = "Mark selected as Paid"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'price', 'quantity']

# ==========================================
# 6. CUSTOMIZING ADMIN PANEL LOOK
# ==========================================
admin.site.site_header = "Apna Mart Admin"
admin.site.site_title = "Apna Mart Portal"
admin.site.index_title = "Welcome to Shop Management"