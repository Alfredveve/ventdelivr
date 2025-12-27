import os
import django
from decimal import Decimal

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ventdelivr.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.models import Order
from catalog.models import Product, Category
from merchants.models import MerchantProfile
from finance.models import Wallet, Transaction, Commission
from finance.services import FinanceService
from orders.services import OrderService
from delivery.services import DeliveryService
from django.db import transaction

User = get_user_model()

def verify_flow():
    print("=== Début de la vérification financière ===")
    
    # 1. Setup - Création des acteurs
    with transaction.atomic():
        # Nettoyage rapide (optionnel en dev)
        # Transaction.objects.all().delete()
        
        # Le client
        customer, _ = User.objects.get_or_create(username='test_customer_fin')
        customer_wallet, _ = Wallet.objects.get_or_create(user=customer)
        customer_wallet.balance = Decimal('1000.00')
        customer_wallet.save()
        
        # Le marchand
        merchant_user, _ = User.objects.get_or_create(username='test_merchant_fin')
        merchant_profile, _ = MerchantProfile.objects.get_or_create(
            user=merchant_user, 
            defaults={'store_name': 'Finance Store', 'is_verified': True}
        )
        merchant_wallet, _ = Wallet.objects.get_or_create(user=merchant_user)
        merchant_wallet.balance = Decimal('0.00')
        merchant_wallet.save()
        
        # La commission (10%)
        Commission.objects.all().delete()
        Commission.objects.create(name="Frais Platforme Test", rate=Decimal('10.00'), is_active=True)
        
        # Le produit
        category, _ = Category.objects.get_or_create(name='Uncategorized')
        product, _ = Product.objects.get_or_create(
            name='Produit de test finance',
            defaults={
                'merchant': merchant_profile,
                'category': category,
                'price': Decimal('500.00'),
                'is_available': True
            }
        )
        if not hasattr(product, 'inventory'):
            from catalog.models import Inventory
            Inventory.objects.create(product=product, quantity=100)

    print(f"Setups terminés. Solde Client: {customer_wallet.balance}, Solde Marchand: {merchant_wallet.balance}")

    # 2. Passage de commande
    items = [{'product_id': product.id, 'quantity': 1}]
    order = OrderService.place_order(customer, items)
    print(f"Commande #{order.id} créée. Total: {order.total_price}")

    # 3. Paiement
    OrderService.fulfill_order(order.id)
    customer_wallet.refresh_from_db()
    print(f"Commande payée. Nouveau solde Client: {customer_wallet.balance}")
    assert customer_wallet.balance == Decimal('500.00')

    # 4. Création et finalisation de livraison
    delivery = DeliveryService.create_delivery(order)
    delivery.status = delivery.Status.IN_TRANSIT # Bypass intermediate steps for test
    delivery.save()
    
    # Finalisation (déclenche payout)
    DeliveryService.complete_delivery(delivery.id, delivery.delivery_code)
    
    # 5. Vérification finale
    merchant_wallet.refresh_from_db()
    
    # 500 - 10% (50) = 450
    expected_merchant_balance = Decimal('450.00')
    print(f"Livraison terminée. Nouveau solde Marchand: {merchant_wallet.balance}")
    
    if merchant_wallet.balance == expected_merchant_balance:
        print("✅ SUCCÈS: Versement marchand correct (450.00)")
    else:
        print(f"❌ ERREUR: Versement incorrect. Attendu {expected_merchant_balance}, obtenu {merchant_wallet.balance}")

    # Vérification des transactions
    transactions = Transaction.objects.filter(order=order)
    print("\nRécapitulatif des transactions pour cette commande:")
    for t in transactions:
        print(f"- {t.get_label_display()}: {t.amount} ({t.wallet.user.username})")

    print("=== Fin de la vérification ===")

if __name__ == "__main__":
    verify_flow()
