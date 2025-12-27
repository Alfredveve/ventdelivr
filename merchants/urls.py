from django.urls import path
from . import views

app_name = 'merchants'

urlpatterns = [
    path('dashboard/', views.MerchantDashboardView.as_view(), name='dashboard'),
    path('products/', views.MerchantProductListView.as_view(), name='product_list'),
    path('products/add/', views.MerchantProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/edit/', views.MerchantProductUpdateView.as_view(), name='product_update'),
    path('<slug:slug>/', views.MerchantDetailView.as_view(), name='detail'),
]
