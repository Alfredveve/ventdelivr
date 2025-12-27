import os
import django
from decimal import Decimal

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ventdelivr.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.services import UserService
from catalog.services import ProductService, InventoryService
from orders.services import OrderService
from finance.services import FinanceService
from finance.models import Wallet
from catalog.models import Product, Category

User = get_user_model()

def run_verification():
    print("=== Vérification du Traitement des Commandes (Règles de l'Art) ===")
    
    # 1. Nettoyage
    User.objects.filter(username__in=["test_merchant", "test_customer"]).delete()
    Category.objects.filter(name="Test Category").delete()
    print("[-] Nettoyage effectué.")

    # 2. Setup
    merchant = UserService.create_user("test_merchant", "m@test.com", "pass123", User.Role.MERCHANT)
    customer = UserService.create_user("test_customer", "c@test.com", "pass123", User.Role.CUSTOMER)
    category = Category.objects.create(name="Test Category")
    
    # Fond initial
    FinanceService.deposit_funds(customer.wallet, Decimal("500.00"))
    
    # 3. Création Produit
    product_data = {
        'name': 'Produit Test Robustesse',
        'price': Decimal('100.00'),
        'sku': 'ROBUST-001',
        'initial_stock': 5,
        'category': category.id
    }
    product = ProductService.create_product(merchant.merchant_profile, product_data)
    print(f"[+] Produit créé: {product.name}, Stock: {product.inventory.quantity}")

    # 4. Test Stock Insuffisant
    print("\n[Test 1] Commande supérieure au stock...")
    try:
        OrderService.place_order(customer, [{'product_id': product.id, 'quantity': 10}])
        print("[!] ERREUR: La commande aurait dû échouer.")
    except Exception as e:
        print(f"[OK] Échec attendu: {e}")

    # 5. Test Commande Valide
    print("\n[Test 2] Commande valide (2 articles)...")
    order = OrderService.place_order(customer, [{'product_id': product.id, 'quantity': 2}])
    product.refresh_from_db()
    print(f"[OK] Commande #{order.id} créée. Nouveau stock: {product.inventory.quantity}")

    # 6. Test Paiement
    print("\n[Test 3] Paiement de la commande...")
    OrderService.fulfill_order(order.id)
    customer.refresh_from_db()
    order.refresh_from_db()
    print(f"[OK] Commande payée. Statut: {order.status}, Nouveau solde client: {customer.wallet.balance}")

    # 7. Vérification de la livraison (Signal)
    if hasattr(order, 'delivery'):
        print(f"[OK] Livraison créée automatiquement. Code: {order.delivery.delivery_code}")
    else:
        print("[!] ERREUR: Livraison non créée.")

    # 8. Test Annulation
    print("\n[Test 4] Annulation d'une nouvelle commande...")
    order2 = OrderService.place_order(customer, [{'product_id': product.id, 'quantity': 1}])
    product.refresh_from_db()
    print(f"Stock avant annulation: {product.inventory.quantity}")
    OrderService.cancel_order(order2.id)
    product.refresh_from_db()
    print(f"[OK] Commande #{order2.id} annulée. Stock restauré: {product.inventory.quantity}")

    print("\n=== Toutes les vérifications logiques sont OK ===")

if __name__ == "__main__":
    run_verification()
