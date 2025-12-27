import secrets
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Delivery

class DeliveryService:
    """
    Service gérant le cycle de vie des livraisons de manière robuste.
    """

    @staticmethod
    @transaction.atomic
    def create_delivery(order):
        """
        Initialise une livraison pour une commande payée.
        """
        if hasattr(order, 'delivery'):
            return order.delivery

        delivery = Delivery.objects.create(
            order=order,
            status=Delivery.Status.PENDING,
            delivery_code=secrets.token_hex(4).upper(),
            shipping_address=order.customer.address,
            customer_phone=order.customer.phone_number
        )
        return delivery

    @staticmethod
    @transaction.atomic
    def assign_driver(delivery_id, driver):
        """
        Assigne un livreur à une expédition.
        """
        delivery = Delivery.objects.select_for_update().get(id=delivery_id)
        
        if delivery.status in [Delivery.Status.DELIVERED, Delivery.Status.CANCELLED]:
            raise ValidationError(f"La livraison #{delivery_id} ne peut plus être assignée.")
            
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
