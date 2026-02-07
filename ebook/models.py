from django.db import models
from django.contrib.auth.models import User
import uuid # Unique Order ID ke liye

# --- Category & Product Models (Aapka original perfect hai) ---
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True) 
    image = models.ImageField(upload_to='categories/')
    
    class Meta:
        verbose_name_plural = "Categories" # Taaki Admin mein 'Categorys' na dikhe

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
    created_at = models.DateTimeField(auto_now_add=True) # Naya field: Sorting ke liye

    def get_discount(self): # Discount percentage nikalne ke liye
        if self.old_price:
            discount = ((self.old_price - self.price) / self.old_price) * 100
            return int(discount)
        return 0

    def __str__(self):
        return self.name

# --- Order & Order Items (Crucial Addition) ---

class Order(models.Model):
    PAYMENT_CHOICES = (('COD', 'Cash on Delivery'), ('UPI', 'UPI Payment'))
    STATUS_CHOICES = (
        ('Pending', 'Order Placed'),
        ('Packed', 'Packed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4) 
    amount = models.DecimalField(max_digits=10, decimal_places=2) 
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='COD')
    
    # Snapshot of address (Taaki user baad mein profile change kare toh order record na badle)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    pincode = models.CharField(max_length=10, null=True)
    
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    payment_screenshot = models.ImageField(upload_to='payments/', null=True, blank=True)

    def __str__(self):
        return f"Order {self.order_id}"

# YEH ZARURI HAI: Order ke andar kaunse products hain?
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Purchase time ka price
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"