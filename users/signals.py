from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from merchants.models import MerchantProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_related_profiles(sender, instance, created, **kwargs):
    """
    Signal pour créer automatiquement les profils liés lors de la création d'un utilisateur.
    """
    if created:
        if instance.role == User.Role.MERCHANT:
            MerchantProfile.objects.get_or_create(user=instance, store_name=f"Boutique de {instance.username}")
        # On pourrait ajouter ici la création de profils Driver ou Customer si nécessaire
