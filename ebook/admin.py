from django.contrib import admin
from django.utils.html import format_html
# Sabhi models ko sahi se import kiya gaya hai
from .models import Product, Category, CartItem, Order, OrderItem, Wishlist, Slider

# ==========================================
# 1. BASIC MODELS REGISTRATION
# ==========================================
admin.site.register(Slider)
admin.site.register(CartItem)
admin.site.register(Wishlist)

# ==========================================
# 2. CATEGORY ADMIN
# ==========================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

# ==========================================
# 3. ADVANCED PRODUCT ADMIN
# ==========================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Thumbnail dikhane ke liye helper function
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
# 4. PRO ORDER ADMIN
# ==========================================
# OrderItem ko Order ke andar hi dikhane ke liye Inline use kiya hai
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline] # Order ke andar hi items dikhenge
    
    list_display = (
        'order_id', 
        'customer_info', 
        'amount_display', 
        'status', 
        'status_colored', 
        'is_paid', 
        'payment_method',
        'created_at'
    )
    
    list_editable = ('status', 'is_paid') 
    list_filter = ('status', 'is_paid', 'payment_method', 'created_at')
    search_fields = ('order_id', 'full_name', 'phone', 'user__username')
    ordering = ('-created_at',)
    list_per_page = 15

    # Customer details format
    def customer_info(self, obj):
        return format_html('<b>{}</b><br><small>{}</small>', obj.full_name, obj.phone)
    customer_info.short_description = 'Customer'

    # Amount format
    def amount_display(self, obj):
        return format_html('<span style="font-weight: bold;">₹{}</span>', obj.amount)
    amount_display.short_description = 'Total Amount'

    # Status color coding (Visualization ke liye)
    def status_colored(self, obj):
        colors = {
            'Pending': '#ff9800',   # Orange
            'Packed': '#2196f3',    # Blue
            'Shipped': '#9c27b0',   # Purple
            'Delivered': '#4caf50', # Green
            'Cancelled': '#f44336', # Red
        }
        color = colors.get(obj.status, '#000')
        return format_html('<span style="color: {}; font-weight: bold;">● {}</span>', color, obj.status)
    status_colored.short_description = 'Status Indicator'

    # Bulk Action: Ek saath sabko paid mark karne ke liye
    actions = ['mark_as_paid']
    def mark_as_paid(self, request, queryset):
        queryset.update(is_paid=True)
        self.message_user(request, "Selected orders have been marked as Paid.")
    mark_as_paid.short_description = "Mark selected as Paid"

# OrderItem ko alag se bhi register kar diya agar zarurat ho
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'price', 'quantity']

# ==========================================
# 5. CUSTOMIZING ADMIN PANEL LOOK
# ==========================================
admin.site.site_header = "Apna Mart Admin"
admin.site.site_title = "Apna Mart Portal"
admin.site.index_title = "Welcome to Shop Management"