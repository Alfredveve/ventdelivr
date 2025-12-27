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
            MerchantProfile.objects.get_or_create(
                user=instance,
                defaults={
                    'store_name': f"Boutique de {instance.username}",
                    'address': instance.address if instance.address else "Adresse non renseignée"
                }
            )
        
        # Assign user to group based on role
        from django.contrib.auth.models import Group
        group, _ = Group.objects.get_or_create(name=instance.get_role_display())
        instance.groups.add(group)
