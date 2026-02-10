from .models import CartItem, Wishlist
from .models import Category

def category_renderer(request):
    return {
        'categories': Category.objects.all()
    }
def nav_counts(request):
    if request.user.is_authenticated:
        return {
            # User ke cart ke items ka count
            'cart_count': CartItem.objects.filter(user=request.user).count(),
            # User ki wishlist ke items ka count (Aapke model ke hisaab se)
            'wishlist_count': Wishlist.objects.filter(user=request.user).count(),
        }
    return {'cart_count': 0, 'wishlist_count': 0}
