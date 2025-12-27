from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MerchantProfile

@receiver(post_save, sender=MerchantProfile)
def notify_merchant_verification(sender, instance, created, **kwargs):
    """
    Signal pour notifier le marchand de la vérification de son compte.
    """
    if not created and instance.is_verified:
        # On pourrait envoyer un email ici via un MailService
        print(f"Le marchand {instance.store_name} a été vérifié.")
