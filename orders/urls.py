from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='list'),
    path('merchant/', views.merchant_orders, name='merchant_orders'),
    path('<int:order_id>/', views.order_detail, name='detail'),
    path('<int:order_id>/fulfill/', views.order_fulfill, name='fulfill'),
    path('<int:order_id>/cancel/', views.order_cancel, name='cancel'),
    path('<int:order_id>/ship/', views.ship_order, name='ship'),
    path('<int:order_id>/delivered/', views.deliver_order, name='delivered'),
    path('buy/<int:product_id>/', views.quick_buy, name='quick_buy'),
]
