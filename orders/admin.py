from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'customer__username')
    readonly_fields = ('created_at', 'updated_at')
