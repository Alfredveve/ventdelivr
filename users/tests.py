from django.test import TestCase
from django.contrib.auth import get_user_model
from .services import UserService
from merchants.models import MerchantProfile
from finance.models import Wallet

User = get_user_model()

class ArchitectureTestCase(TestCase):
    def test_user_creation_triggers_signals(self):
        """
        Vérifie que la création d'un utilisateur déclenche les bons signaux (Wallet et MerchantProfile).
        """
        # Création d'un marchand via le service
        merchant = UserService.create_user(
            username="testmerchant",
            email="merchant@test.com",
            password="password123",
            role=User.Role.MERCHANT
        )
        
        # Vérification du portefeuille (Finance signal)
        self.assertTrue(Wallet.objects.filter(user=merchant).exists())
        
        # Vérification du profil marchand (Users signal)
        self.assertTrue(MerchantProfile.objects.filter(user=merchant).exists())
        
        # Création d'un client normal
        customer = UserService.create_user(
            username="testcustomer",
            email="customer@test.com",
            password="password123",
            role=User.Role.CUSTOMER
        )
        
        # Le client doit avoir un portefeuille mais PAS de profil marchand
        self.assertTrue(Wallet.objects.filter(user=customer).exists())
        self.assertFalse(MerchantProfile.objects.filter(user=customer).exists())
