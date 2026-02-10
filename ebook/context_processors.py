from .models import CartItem, WishlistItem
from .models import Category

def category_renderer(request):
    return {
        'categories': Category.objects.all()
    }


def nav_counts(request):
    if request.user.is_authenticated:
        return {
            'cart_count': CartItem.objects.filter(user=request.user).count(),
            'wishlist_count': WishlistItem.objects.filter(user=request.user).count(),
        }
    return {'cart_count': 0, 'wishlist_count': 0}