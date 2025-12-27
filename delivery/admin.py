from django.contrib import admin
from .models import Delivery

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'driver', 'status', 'delivery_code', 'assigned_at')
    list_filter = ('status', 'assigned_at')
    search_fields = ('delivery_code', 'order__id', 'driver__username')
