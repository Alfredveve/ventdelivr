from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class UserService:
    """
    Service gérant la logique métier liée aux utilisateurs.
    """
    
    @staticmethod
    @transaction.atomic
    def create_user(username, email, password, role=User.Role.CUSTOMER, **extra_fields):
        """
        Crée un utilisateur de manière sécurisée.
        """
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            **extra_fields
        )
        # Logique supplémentaire (ex: logs d'audit) peut être ajoutée ici
        return user

    @staticmethod
    def update_phone_number(user, new_phone_number):
        """
        Met à jour le numéro de téléphone de l'utilisateur.
        """
        # On pourrait ajouter une vérification par SMS ici
        user.phone_number = new_phone_number
        user.save()
        return user
