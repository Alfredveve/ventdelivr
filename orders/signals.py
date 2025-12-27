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
    if not created and instance.status == Order.Status.PAID:
        # On vérifie si une livraison n'existe pas déjà
        if not hasattr(instance, 'delivery'):
            Delivery.objects.create(
                order=instance,
                delivery_code=secrets.token_hex(4).upper(), # Code sécurisé pour la livraison
                status=Delivery.Status.ASSIGNED
            )
            print(f"Livraison créée pour la commande #{instance.id}")
