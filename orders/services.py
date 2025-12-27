import secrets
from django.db import transaction
from .models import Order

class OrderService:
    """
    Service gérant le cycle de vie des commandes.
    """
    
    @staticmethod
    @transaction.atomic
    def place_order(customer, total_price):
        """
        Crée une nouvelle commande en attente.
        """
        order = Order.objects.create(
            customer=customer,
            total_price=total_price,
            status=Order.Status.PENDING
        )
        return order

    @staticmethod
    @transaction.atomic
    def mark_as_paid(order_id):
        """
        Marque une commande comme payée. 
        Cela déclenchera indirectement la création d'une livraison via les signaux.
        """
        order = Order.objects.get(id=order_id)
        if order.status != Order.Status.PENDING:
            raise ValueError("Seules les commandes en attente peuvent être payées.")
            
        order.status = Order.Status.PAID
        order.save()
        return order
