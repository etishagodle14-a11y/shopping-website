from django.urls import path
from . import views

urlpatterns = [
    # --- Product & Shop ---
    path('', views.product_list, name='product_list'),
    path('all-products/', views.all_products, name='all_products'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('offer-zone/', views.offer_zone, name='offer_zone'),
    
    # --- Authentication ---
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # --- Cart & Wishlist ---
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Ye raha quantity update karne ka path
    path('update-cart/<int:product_id>/<str:action>/', views.update_cart_quantity, name='update_cart_quantity'),
    
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    
    # --- Checkout & Orders ---
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('cancel-order/<str:order_id>/', views.cancel_order, name='cancel_order'),
    path('track-order/<str:order_id>/', views.track_order, name='track_order'),
    
    # --- Gift Cards ---
    path('gift-cards/', views.gift_card_list, name='gift_card_list'),
    path('apply-gift-card/', views.apply_gift_card, name='apply_gift_card'),
]