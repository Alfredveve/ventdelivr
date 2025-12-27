from django.urls import path
from . import views

app_name = 'merchants'

urlpatterns = [
    path('<slug:slug>/', views.MerchantDetailView.as_view(), name='detail'),
]
