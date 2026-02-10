from .models import CartItem
from .models import Category

def category_renderer(request):
    return {
        'categories': Category.objects.all()
    }

def cart_count(request):
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
    else:
        count = 0
    return {'cart_count': count}