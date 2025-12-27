from django.db import transaction
from .models import MerchantProfile

class MerchantService:
    """
    Service gérant la logique métier liée aux marchands.
    """
    
    @staticmethod
    @transaction.atomic
    def verify_merchant(merchant_profile_id, admin_user):
        """
        Valide un marchand (action réservée aux administrateurs).
        """
        if not admin_user.is_staff:
            raise PermissionError("Seuls les administrateurs peuvent valider un marchand.")
            
        profile = MerchantProfile.objects.get(id=merchant_profile_id)
        profile.is_verified = True
        profile.save()
        
        # On pourrait déclencher une notification ici
        return profile

    @staticmethod
    def update_store_info(profile, store_name, description, address):
        """
        Met à jour les informations de la boutique.
        """
        profile.store_name = store_name
        profile.description = description
        profile.address = address
        # Le slug sera mis à jour automatiquement par le modèle .save()
        profile.save()
        return profile
