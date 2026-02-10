from django.urls import path
from . import views

urlpatterns = [
    # Shop & Home
    path('', views.product_list, name='product_list'),
    path('products/', views.all_products, name='all_products'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('search/', views.search_view, name='search'),
    path('offer-zone/', views.offer_zone, name='offer_zone'),

    # Cart & Wishlist
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-item/', views.update_item, name='update_item'),
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    # Wishlist (Dono naam support karne ke liye)
    path('toggle-wishlist/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('add-to-wishlist/<int:product_id>/', views.toggle_wishlist, name='add_to_wishlist'),
    path('increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),

    # Checkout & Orders (YAHAN CHANGE HAI)
    # Buy Now click karne par hamesha 'checkout_single' wala path hit hona chahiye
    path('checkout/', views.checkout, name='checkout'), # Cart ke liye
    path('checkout/<int:product_id>/', views.checkout, name='checkout_single'),# Single item ke liye
    
    path('place-order/', views.place_order, name='place_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('remove-from-checkout/<int:item_id>/', views.remove_from_checkout, name='remove_from_checkout'),
    path('order-success/<str:order_id>/', views.order_success, name='order_success'),
    path('track-order/<str:order_id>/', views.track_order, name='track_order'),
    path('cancel-order/<str:order_id>/', views.cancel_order, name='cancel_order'),

    # Auth
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]