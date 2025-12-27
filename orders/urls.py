from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Cart URLs
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
    
    # Order URLs
    path('', views.order_list, name='list'),
    path('merchant/', views.merchant_orders, name='merchant_orders'),
    path('<int:order_id>/', views.order_detail, name='detail'),
    path('<int:order_id>/fulfill/', views.order_fulfill, name='fulfill'),
    path('<int:order_id>/cancel/', views.order_cancel, name='cancel'),
    path('<int:order_id>/ship/', views.ship_order, name='ship'),
    path('<int:order_id>/delivered/', views.deliver_order, name='delivered'),
    path('buy/<int:product_id>/', views.quick_buy, name='quick_buy'),
]
