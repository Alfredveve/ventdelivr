# -*- coding: utf-8 -*-
"""
Script de vérification pour la logistique de livraison.
Teste:
- Calcul des frais de livraison
- Géocodage des adresses
- Attribution automatique des livreurs
- Mise à jour de la localisation
"""

import os
import django
from contextlib import contextmanager

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ventdelivr.settings')
django.setup()

from django.db import transaction
from django.db.models.signals import post_save
from users.models import User
from catalog.models import Product
from orders.models import Order, OrderItem
from delivery.models import Delivery
from delivery.services import DeliveryService
from delivery.google_maps import GoogleMapsService
from decimal import Decimal

@contextmanager
def disable_signals():
    """Temporarily disable all post_save signals"""
    saved_receivers = post_save.receivers
    post_save.receivers = []
    try:
        yield
    finally:
        post_save.receivers = saved_receivers

def test_google_maps_service():
    """Test du service Google Maps (mock)"""
    print("\n=== Test Google Maps Service ===")
    
    # Test geocoding
    coords = GoogleMapsService.geocode_address("123 Rue de Paris")
    print(f"✓ Geocoding: lat={coords['lat']}, lng={coords['lng']}")
    
    # Test distance calculation
    distance = GoogleMapsService.calculate_distance(
        48.8566, 2.3522,  # Paris
        48.8606, 2.3376   # Arc de Triomphe
    )
    print(f"✓ Distance calculée: {distance} km")
    
    # Test fee calculation
    fee = GoogleMapsService.calculate_delivery_cost(5.5)
    print(f"✓ Frais pour 5.5 km: {fee} FCFA")

def test_delivery_creation_with_fee():
    """Test de création de livraison avec calcul de frais"""
    print("\n=== Test Création Livraison avec Frais ===")
    
    with disable_signals(), transaction.atomic():
        # Create test customer
        customer = User.objects.filter(role=User.Role.CUSTOMER).first()
        if not customer:
            customer = User.objects.create_user(
                username='test_customer_delivery',
                password='test123',
                role=User.Role.CUSTOMER,
                address='10 Avenue des Champs-Élysées, Paris',
                phone_number='+33123456789'
            )
            print(f"✓ Client créé: {customer.username}")
        
        # Create test merchant and product
        from merchants.models import MerchantProfile
        
        merchant_user = User.objects.filter(role=User.Role.MERCHANT).first()
        if not merchant_user:
            merchant_user = User.objects.create_user(
                username='test_merchant_delivery',
                password='test123',
                role=User.Role.MERCHANT,
                address='5 Rue de Rivoli, Paris'
            )
        
        merchant_profile = MerchantProfile.objects.filter(user=merchant_user).first()
        if not merchant_profile:
            merchant_profile = MerchantProfile.objects.create(
                user=merchant_user,
                store_name='Test Store Delivery',
                address='5 Rue de Rivoli, Paris'
            )
        
        product = Product.objects.filter(merchant=merchant_profile).first()
        if not product:
            product = Product.objects.create(
                name='Test Product Delivery',
                merchant=merchant_profile,
                price=Decimal('1000.00'),
                sku='TEST-DELIVERY-001'
            )
            print(f"✓ Produit créé: {product.name}")
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            total_price=Decimal('1000.00'),
            status=Order.Status.PAID
        )
        
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            price=product.price
        )
        print(f"✓ Commande créée: #{order.id}")
        
        # Create delivery with fee calculation
        delivery = DeliveryService.create_delivery(order)
        
        print(f"✓ Livraison créée: #{delivery.id}")
        print(f"  - Code: {delivery.delivery_code}")
        print(f"  - Frais: {delivery.delivery_fee} FCFA")
        print(f"  - Pickup: ({delivery.pickup_latitude}, {delivery.pickup_longitude})")
        print(f"  - Dropoff: ({delivery.dropoff_latitude}, {delivery.dropoff_longitude})")
        
        # Cleanup
        transaction.set_rollback(True)

def test_driver_allocation():
    """Test de l'attribution automatique de livreur"""
    print("\n=== Test Attribution Automatique Livreur ===")
    
    with disable_signals(), transaction.atomic():
        from merchants.models import MerchantProfile
        
        # Create test drivers
        drivers_created = []
        for i in range(3):
            driver = User.objects.create_user(
                username=f'test_driver_{i}',
                password='test123',
                role=User.Role.DRIVER,
                address=f'{i*10} Rue Test, Paris'
            )
            drivers_created.append(driver)
            print(f"✓ Livreur créé: {driver.username}")
        
        # Find available drivers
        available = DeliveryService.find_available_drivers(48.8566, 2.3522)
        print(f"✓ Livreurs disponibles trouvés: {len(available)}")
        
        # Create test delivery
        customer = User.objects.create_user(
            username='test_customer_alloc',
            password='test123',
            role=User.Role.CUSTOMER,
            address='Test Address'
        )
        
        merchant_user = User.objects.create_user(
            username='test_merchant_alloc',
            password='test123',
            role=User.Role.MERCHANT,
            address='Merchant Address'
        )
        
        merchant_profile = MerchantProfile.objects.create(
            user=merchant_user,
            store_name='Test Store Alloc',
            address='Merchant Address'
        )
        
        product = Product.objects.create(
            name='Test Product Alloc',
            merchant=merchant_profile,
            price=Decimal('500.00'),
            sku='TEST-ALLOC-001'
        )
        
        order = Order.objects.create(
            customer=customer,
            total_price=Decimal('500.00'),
            status=Order.Status.PAID
        )
        
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            price=product.price
        )
        
        delivery = DeliveryService.create_delivery(order)
        print(f"✓ Livraison créée: #{delivery.id}")
        
        # Auto-assign driver
        delivery = DeliveryService.assign_driver(delivery.id)
        print(f"✓ Livreur assigné automatiquement: {delivery.driver.username}")
        
        # Cleanup
        transaction.set_rollback(True)

def test_location_tracking():
    """Test de mise à jour de localisation"""
    print("\n=== Test Suivi de Localisation ===")
    
    with disable_signals(), transaction.atomic():
        from merchants.models import MerchantProfile
        
        # Create complete delivery scenario
        customer = User.objects.create_user(
            username='test_customer_track',
            password='test123',
            role=User.Role.CUSTOMER,
            address='Customer Address'
        )
        
        driver = User.objects.create_user(
            username='test_driver_track',
            password='test123',
            role=User.Role.DRIVER,
            address='Driver Address'
        )
        
        merchant_user = User.objects.create_user(
            username='test_merchant_track',
            password='test123',
            role=User.Role.MERCHANT,
            address='Merchant Address'
        )
        
        merchant_profile = MerchantProfile.objects.create(
            user=merchant_user,
            store_name='Test Store Track',
            address='Merchant Address'
        )
        
        product = Product.objects.create(
            name='Test Product Track',
            merchant=merchant_profile,
            price=Decimal('750.00'),
            sku='TEST-TRACK-001'
        )
        
        order = Order.objects.create(
            customer=customer,
            total_price=Decimal('750.00'),
            status=Order.Status.PAID
        )
        
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            price=product.price
        )
        
        delivery = DeliveryService.create_delivery(order)
        delivery = DeliveryService.assign_driver(delivery.id, driver)
        print(f"✓ Livraison créée et assignée: #{delivery.id}")
        
        # Mark as ready and pickup
        delivery = DeliveryService.mark_as_ready(delivery.id, "Colis prêt")
        delivery = DeliveryService.pickup_package(delivery.id, "Colis récupéré")
        print(f"✓ Statut: {delivery.status}")
        
        # Update location
        delivery = DeliveryService.update_driver_location(
            delivery.id,
            48.8606,  # New latitude
            2.3376    # New longitude
        )
        print(f"✓ Position mise à jour: ({delivery.current_latitude}, {delivery.current_longitude})")
        print(f"  - Dernière mise à jour: {delivery.last_location_update}")
        
        # Cleanup
        transaction.set_rollback(True)

if __name__ == '__main__':
    print("=" * 60)
    print("VÉRIFICATION: LOGISTIQUE DE LIVRAISON")
    print("=" * 60)
    
    try:
        test_google_maps_service()
        test_delivery_creation_with_fee()
        test_driver_allocation()
        test_location_tracking()
        
        print("\n" + "=" * 60)
        print("✓ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
