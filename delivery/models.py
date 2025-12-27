from django.db import models
from django.conf import settings
from orders.models import Order

class Delivery(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        READY_FOR_PICKUP = 'READY', 'Prêt pour ramassage'
        PICKED_UP = 'PICKED_UP', 'Récupéré'
        IN_TRANSIT = 'IN_TRANSIT', 'En cours de livraison'
        DELIVERED = 'DELIVERED', 'Livré'
        CANCELLED = 'CANCELLED', 'Annulé'
        FAILED = 'FAILED', 'Échoué'

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='delivery'
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    delivery_code = models.CharField(max_length=10, blank=True)
    
    # Tracking fields
    shipping_address = models.TextField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    
    merchant_notes = models.TextField(blank=True)
    driver_notes = models.TextField(blank=True)
    
    assigned_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    
    # Financials
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Location Data (Geocoordinates)
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    dropoff_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    dropoff_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Real-time Driver Location
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Livraison pour la Commande #{self.order.id} - {self.get_status_display()}"
