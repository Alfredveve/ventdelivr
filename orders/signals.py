import secrets
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from delivery.models import Delivery

@receiver(post_save, sender=Order)
def trigger_delivery_creation(sender, instance, created, **kwargs):
    """
    Signal pour créer automatiquement une livraison quand une commande est payée.
    """
    from delivery.services import DeliveryService
    
    if not created and instance.status == Order.Status.PAID:
        # On vérifie si une livraison n'existe pas déjà
        if not hasattr(instance, 'delivery'):
            DeliveryService.create_delivery(instance)
            print(f"Logistique de livraison initialisée pour la commande #{instance.id}")
