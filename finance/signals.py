from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Wallet

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """
    Signal pour créer automatiquement un portefeuille à chaque nouvel utilisateur.
    """
    if created:
        Wallet.objects.get_or_create(user=instance)
        print(f"Portefeuille créé pour {instance.username}")
