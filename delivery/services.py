import secrets
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from .models import Delivery
from .google_maps import GoogleMapsService

class DeliveryService:
    """
    Service gérant le cycle de vie des livraisons de manière robuste.
    """

    @staticmethod
    @transaction.atomic
    def create_delivery(order):
        """
        Initialise une livraison pour une commande payée.
        Calcule les frais de livraison et géocode les adresses.
        """
        if hasattr(order, 'delivery'):
            return order.delivery

        # Geocode shipping address (customer)
        customer_coords = GoogleMapsService.geocode_address(order.customer.address)
        
        # Geocode merchant address (pickup location)
        merchant_profile = order.items.first().product.merchant if order.items.exists() else None
        merchant_address = merchant_profile.address if merchant_profile else "Default Merchant Location"
        merchant_coords = GoogleMapsService.geocode_address(merchant_address)
        
        # Calculate distance
        distance_km = GoogleMapsService.calculate_distance(
            merchant_coords['lat'], merchant_coords['lng'],
            customer_coords['lat'], customer_coords['lng']
        )
        
        # Calculate delivery fee
        delivery_fee = GoogleMapsService.calculate_delivery_cost(distance_km)

        delivery = Delivery.objects.create(
            order=order,
            status=Delivery.Status.PENDING,
            delivery_code=secrets.token_hex(4).upper(),
            shipping_address=order.customer.address,
            customer_phone=order.customer.phone_number,
            delivery_fee=delivery_fee,
            pickup_latitude=merchant_coords['lat'],
            pickup_longitude=merchant_coords['lng'],
            dropoff_latitude=customer_coords['lat'],
            dropoff_longitude=customer_coords['lng']
        )
        return delivery

    @staticmethod
    def find_available_drivers(pickup_lat, pickup_lng, limit=5):
        """
        Trouve les livreurs disponibles triés par distance du point de ramassage.
        """
        from users.models import User
        
        drivers = User.objects.filter(role=User.Role.DRIVER, is_active=True)
        
        # Calculate distance for each driver (mock: assume drivers have addresses)
        driver_distances = []
        for driver in drivers:
            if driver.address:
                driver_coords = GoogleMapsService.geocode_address(driver.address)
                distance = GoogleMapsService.calculate_distance(
                    pickup_lat, pickup_lng,
                    driver_coords['lat'], driver_coords['lng']
                )
                driver_distances.append((driver, distance))
        
        # Sort by distance
        driver_distances.sort(key=lambda x: x[1])
        
        return [d[0] for d in driver_distances[:limit]]

    @staticmethod
    @transaction.atomic
    def assign_driver(delivery_id, driver=None):
        """
        Assigne un livreur à une expédition.
        Si driver=None, sélectionne automatiquement le livreur le plus proche.
        """
        delivery = Delivery.objects.select_for_update().get(id=delivery_id)
        
        if delivery.status in [Delivery.Status.DELIVERED, Delivery.Status.CANCELLED]:
            raise ValidationError(f"La livraison #{delivery_id} ne peut plus être assignée.")
        
        # Auto-assign if no driver provided
        if driver is None:
            available_drivers = DeliveryService.find_available_drivers(
                delivery.pickup_latitude, delivery.pickup_longitude
            )
            if not available_drivers:
                raise ValidationError("Aucun livreur disponible.")
            driver = available_drivers[0]
            
        delivery.driver = driver
        delivery.assigned_at = timezone.now()
        delivery.save()
        return delivery

    @staticmethod
    @transaction.atomic
    def mark_as_ready(delivery_id, merchant_notes=""):
        """
        Le marchand indique que le colis est prêt à être récupéré.
        """
        delivery = Delivery.objects.select_for_update().get(id=delivery_id)
        
        if delivery.status != Delivery.Status.PENDING:
             raise ValidationError(f"La livraison #{delivery_id} n'est pas en attente.")
             
        delivery.status = Delivery.Status.READY_FOR_PICKUP
        delivery.ready_at = timezone.now()
        delivery.merchant_notes = merchant_notes
        delivery.save()
        return delivery

    @staticmethod
    @transaction.atomic
    def pickup_package(delivery_id, driver_notes=""):
        """
        Le livreur confirme qu'il a récupéré le colis chez le marchand.
        """
        delivery = Delivery.objects.select_for_update().get(id=delivery_id)
        
        if delivery.status != Delivery.Status.READY_FOR_PICKUP:
            raise ValidationError(f"Le colis n'est pas encore prêt pour le ramassage.")
            
        if not delivery.driver:
            raise ValidationError(f"Aucun livreur n'est assigné à cette livraison.")

        delivery.status = Delivery.Status.PICKED_UP
        delivery.picked_up_at = timezone.now()
        delivery.driver_notes = driver_notes
        delivery.save()
        
        # On passe automatiquement en transit
        delivery.status = Delivery.Status.IN_TRANSIT
        delivery.save()
        
        return delivery

    @staticmethod
    @transaction.atomic
    def complete_delivery(delivery_id, otp_code):
        """
        Finalise la livraison après vérification du code de sécurité.
        """
        delivery = Delivery.objects.select_for_update().get(id=delivery_id)
        
        if delivery.status != Delivery.Status.IN_TRANSIT:
            raise ValidationError(f"La livraison n'est pas en cours (statut actuel: {delivery.status}).")
            
        if delivery.delivery_code != otp_code:
            raise ValidationError("Code de livraison incorrect.")

        delivery.status = Delivery.Status.DELIVERED
        delivery.delivered_at = timezone.now()
        delivery.save()
        
        # Mettre à jour le statut de la commande également
        from orders.models import Order
        order = delivery.order
        order.status = Order.Status.DELIVERED
        order.save()
        
        # Déclenchement du versement au marchand (Logique financière)
        from finance.services import FinanceService
        FinanceService.settle_merchant_payout(order)
        
        return delivery

    @staticmethod
    @transaction.atomic
    def update_driver_location(delivery_id, latitude, longitude):
        """
        Met à jour la position actuelle du livreur.
        """
        delivery = Delivery.objects.select_for_update().get(id=delivery_id)
        
        if delivery.status not in [Delivery.Status.PICKED_UP, Delivery.Status.IN_TRANSIT]:
            raise ValidationError("Le suivi de localisation n'est actif que pendant le transport.")
        
        delivery.current_latitude = latitude
        delivery.current_longitude = longitude
        delivery.last_location_update = timezone.now()
        delivery.save()
        
        return delivery

    @staticmethod
    @transaction.atomic
    def cancel_delivery(delivery_id, reason=""):
        """
        Annule une livraison.
        """
        delivery = Delivery.objects.select_for_update().get(id=delivery_id)
        
        if delivery.status in [Delivery.Status.DELIVERED, Delivery.Status.CANCELLED]:
            raise ValidationError("Cette livraison ne peut plus être annulée.")
            
        delivery.status = Delivery.Status.CANCELLED
        delivery.driver_notes = f"ANNULATION: {reason}"
        delivery.save()
        
        return delivery
