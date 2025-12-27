import os
import django
import sys

# Configuration de Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ventdelivr.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.services import OrderService
from orders.models import Order
from delivery.models import Delivery
from delivery.services import DeliveryService
from catalog.models import Product, Inventory, Category
from finance.models import Wallet
from merchants.models import MerchantProfile

User = get_user_model()

def run_verification():
    print("=== Début de la vérification du système de livraison ===")
    
    # 1. Préparation des données
    customer, _ = User.objects.get_or_create(username="test_customer", defaults={'role': User.Role.CUSTOMER, 'address': '123 Plateau, Abidjan', 'phone_number': '+2250102030405'})
    driver, _ = User.objects.get_or_create(username="test_driver", defaults={'role': User.Role.DRIVER})
    merchant, _ = User.objects.get_or_create(username="test_merchant", defaults={'role': User.Role.MERCHANT})
    merchant_profile, _ = MerchantProfile.objects.get_or_create(user=merchant, defaults={'store_name': 'Test Store', 'address': 'Abidjan'})
    
    # Assurer que le client a de l'argent
    wallet, _ = Wallet.objects.get_or_create(user=customer, defaults={'balance': 10000})
    wallet.balance = 10000
    wallet.save()
    
    # Créer un produit
    category, _ = Category.objects.get_or_create(name="Food")
    product, _ = Product.objects.get_or_create(
        name="Attiéké Premium",
        defaults={'merchant': merchant_profile, 'price': 500, 'category': category, 'sku': 'ATK-001'}
    )
    inventory, _ = Inventory.objects.get_or_create(product=product, defaults={'quantity': 100})
    inventory.quantity = 100
    inventory.save()
    
    print(f"1. Client {customer.username} et Produit {product.name} prêts.")

    # 2. Passer une commande
    items = [{'product_id': product.id, 'quantity': 2}]
    order = OrderService.place_order(customer, items)
    print(f"2. Commande #{order.id} créée. Statut: {order.get_status_display()}")

    # 3. Payer la commande (ceci devrait déclencher la création de la livraison via signal)
    OrderService.fulfill_order(order.id)
    order.refresh_from_db()
    print(f"3. Commande #{order.id} payée. Statut: {order.get_status_display()}")
    
    delivery = Delivery.objects.get(order=order)
    print(f"   -> Livraison créée automatiquement. Statut: {delivery.get_status_display()}")
    print(f"   -> Code de livraison (OTP): {delivery.delivery_code}")

    # 4. Assigner un livreur
    DeliveryService.assign_driver(delivery.id, driver)
    delivery.refresh_from_db()
    print(f"4. Livreur {driver.username} assigné. Statut livraison: {delivery.get_status_display()}")

    # 5. Marchand marque comme prêt
    OrderService.ship_order(order.id, merchant_notes="Emballé avec soin")
    delivery.refresh_from_db()
    print(f"5. Marchand a marqué prêt. Statut livraison: {delivery.get_status_display()}")

    # 6. Livreur récupère le colis
    DeliveryService.pickup_package(delivery.id, driver_notes="Colis récupéré au Plateau")
    delivery.refresh_from_db()
    print(f"6. Livreur a récupéré le colis. Statut livraison: {delivery.get_status_display()}")

    # 7. Tenter de finaliser avec un mauvais code (doit échouer)
    print("7. Test d'un mauvais code OTP...")
    try:
        DeliveryService.complete_delivery(delivery.id, "WRONG")
    except Exception as e:
        print(f"   -> Échec attendu réussi: {e}")

    # 8. Finaliser avec le bon code
    DeliveryService.complete_delivery(delivery.id, delivery.delivery_code)
    delivery.refresh_from_db()
    order.refresh_from_db()
    print(f"8. Livraison finalisée avec succès. Statut livraison: {delivery.get_status_display()}")
    print(f"   -> Statut final de la commande: {order.get_status_display()}")

    print("=== Vérification terminée avec SUCCÈS ===")

if __name__ == "__main__":
    run_verification()
