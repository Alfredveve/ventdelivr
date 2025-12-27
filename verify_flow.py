import os
import django
from decimal import Decimal

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ventdelivr.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.services import UserService
from merchants.models import MerchantProfile
from orders.services import OrderService
from finance.services import FinanceService
from finance.models import Wallet

User = get_user_model()

def run_verification():
    print("=== Démarrage de la vérification du flux complet ===")
    
    # 1. Nettoyage (pour la démo)
    username_merchant = "demo_merchant"
    username_customer = "demo_customer"
    User.objects.filter(username__in=[username_merchant, username_customer]).delete()
    print("[-] Données de test précédentes nettoyées.")

    # 2. Création du Marchand
    print("\n[1] Création du compte Marchand...")
    merchant = UserService.create_user(
        username=username_merchant,
        email="merchant@demo.com",
        password="SecurePassword123!",
        role=User.Role.MERCHANT
    )
    # Vérification du profil marchand (Signal)
    try:
        profile = merchant.merchant_profile
        print(f"[+] Profil marchand créé automatiquement : {profile.store_name}")
    except MerchantProfile.DoesNotExist:
        print("[!] ERREUR : Le profil marchand n'a pas été créé !")
        return

    # 3. Création du Client
    print("\n[2] Création du compte Client...")
    customer = UserService.create_user(
        username=username_customer,
        email="customer@demo.com",
        password="SecurePassword123!",
        role=User.Role.CUSTOMER
    )
    # Vérification du portefeuille (Signal)
    try:
        wallet = customer.wallet
        print(f"[+] Portefeuille client créé automatiquement. Solde initial : {wallet.balance}")
    except Wallet.DoesNotExist:
        print("[!] ERREUR : Le portefeuille client n'a pas été créé !")
        return

    # 4. Ajout de fonds au portefeuille
    print("\n[3] Ajout de fonds (150.00)...")
    FinanceService.deposit_funds(wallet, Decimal("150.00"))
    print(f"[+] Nouveau solde : {customer.wallet.balance}")

    # 5. Passage d'une commande
    print("\n[4] Passage d'une commande (Montant: 100.00)...")
    order = OrderService.place_order(customer, Decimal("100.00"))
    print(f"[+] Commande #{order.id} créée. Statut : {order.status}")

    # 6. Paiement de la commande
    print("\n[5] Paiement de la commande...")
    try:
        # Débit du portefeuille
        FinanceService.process_payment(customer.wallet, order.total_price, order)
        # Mise à jour statut commande
        OrderService.mark_as_paid(order.id)
        
        # Re-fetch pour voir les mises à jour
        customer.refresh_from_db()
        order.refresh_from_db()
        
        print(f"[+] Paiement accepté. Nouveau solde : {customer.wallet.balance}")
        print(f"[+] Statut commande : {order.status}")
        
    except Exception as e:
        print(f"[!] Erreur lors du paiement : {e}")
        return

    # 7. Vérification de la livraison générée (Signal)
    print("\n[6] Vérification de la livraison automatique...")
    if hasattr(order, 'delivery'):
        delivery = order.delivery
        print(f"[+] Livraison générée avec succès !")
        print(f"    - Code de livraison : {delivery.delivery_code}")
        print(f"    - Statut : {delivery.status}")
    else:
        print("[!] ERREUR : Aucune livraison n'a été générée pour la commande payée !")

    print("\n=== Vérification terminée avec succès ===")

if __name__ == "__main__":
    run_verification()
