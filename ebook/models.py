from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# ==========================================
# 1. CATEGORY & PRODUCT MODELS
# ==========================================

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True) 
    image = models.ImageField(upload_to='categories/')

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='products/')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField()
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# ==========================================
# 2. MARKETING & PROMOTION MODELS
# ==========================================

class Slider(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='sliders/')
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title if self.title else f"Slider {self.id}"

class GiftCard(models.Model):
    code = models.CharField(max_length=20, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True) 

    def __str__(self):
        return f"{self.code} - ₹{self.amount}"

# ==========================================
# 3. USER INTERACTION MODELS
# ==========================================

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.product.price

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

# ==========================================
# 4. CHECKOUT & ORDER MODELS
# ==========================================

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=15)
    pincode = models.CharField(max_length=10)
    locality = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.full_name} - {self.city}"

class Order(models.Model):
    PAYMENT_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('UPI', 'UPI Payment'),  # views.py ke hisab se 'Online' ko 'UPI' kar diya hai
    )
    
    STATUS_CHOICES = (
        ('Pending', 'Order Placed'),
        ('Packed', 'Packed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, unique=True) # Unique add kiya hai
    amount = models.DecimalField(max_digits=10, decimal_places=2) # Float se Decimal behtar hai money ke liye
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='COD')
    
    # Address Fields
    full_name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_screenshot = models.ImageField(upload_to='payments/', null=True, blank=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.user.username}"