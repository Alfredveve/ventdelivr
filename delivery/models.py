from django.db import models
from django.conf import settings
from orders.models import Order

class Delivery(models.Model):
    class Status(models.TextChoices):
        ASSIGNED = 'ASSIGNED', 'Assigned'
        PICKED_UP = 'PICKED_UP', 'Picked Up'
        DELIVERED = 'DELIVERED', 'Delivered'

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
        default=Status.ASSIGNED
    )
    delivery_code = models.CharField(max_length=10, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Delivery for Order #{self.order.id}"
