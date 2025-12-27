import secrets
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Order, OrderItem
from catalog.models import Product
from catalog.services import InventoryService, InsufficientStockError
from finance.services import FinanceService, InsufficientFundsError

class OrderService:
    """
    Service gérant le cycle de vie des commandes "dans les règles de l'art".
    """
    
    @staticmethod
    @transaction.atomic
    def place_order(customer, items_data):
        """
        Crée une nouvelle commande et réserve les stocks.
        items_data: list of dict {'product_id': id, 'quantity': q}
        """
        if not items_data:
            raise ValidationError("Une commande doit contenir au moins un article.")

        # 1. Préparer les données et valider les prix/stocks
        items_to_create = []
        total_price = 0
        
        for item in items_data:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            
            try:
                product = Product.objects.select_related('inventory').get(id=product_id)
            except Product.DoesNotExist:
                raise ValidationError(f"Le produit avec l'ID {product_id} n'existe pas.")

            if not product.is_available:
                raise ValidationError(f"Le produit {product.name} n'est plus disponible.")

            # 2. Réserver le stock (débit immédiat pour éviter les race conditions)
            InventoryService.adjust_stock(product, -quantity)
            
            price = product.discount_price if product.discount_price else product.price
            item_total = price * quantity
            total_price += item_total
            
            items_to_create.append({
                'product': product,
                'quantity': quantity,
                'price': price
            })

        # 3. Créer la commande
        order = Order.objects.create(
            customer=customer,
            total_price=total_price,
            status=Order.Status.PENDING
        )

        # 4. Créer les articles de la commande
        for item in items_to_create:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )

        return order

    @staticmethod
    @transaction.atomic
    def fulfill_order(order_id):
        """
        Procède au paiement et valide la commande.
        """
        order = Order.objects.select_related('customer__wallet').get(id=order_id)
        
        if order.status != Order.Status.PENDING:
            raise ValidationError(f"La commande #{order.id} ne peut pas être payée (statut actuel: {order.status}).")

        # Paiement via le service finance robuste
        FinanceService.process_order_payment(order)
        
        # Mise à jour du statut
        order.status = Order.Status.PAID
        order.save()
        
        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(order_id, reason=""):
        """
        Annule une commande et restaure les stocks.
        """
        order = Order.objects.get(id=order_id)
        
        if order.status in [Order.Status.DELIVERED, Order.Status.CANCELLED]:
            raise ValidationError(f"La commande #{order.id} ne peut plus être annulée.")

        # 1. Restaurer les stocks
        for item in order.items.all():
            InventoryService.adjust_stock(item.product, item.quantity)

        # 2. Rembourser si payé
        if order.status == Order.Status.PAID:
            FinanceService.deposit_funds(
                order.customer.wallet, 
                order.total_price, 
                description=f"Remboursement commande #{order.id}"
            )

        # 3. Changer le statut
        order.status = Order.Status.CANCELLED
        order.save()
        
        return order

    @staticmethod
    @transaction.atomic
    def ship_order(order_id, merchant_notes=""):
        """
        Le marchand prépare la commande et la marque comme prête pour le ramassage.
        """
        from delivery.services import DeliveryService
        order = Order.objects.get(id=order_id)
        
        if order.status != Order.Status.PAID:
            raise ValidationError(f"La commande #{order.id} doit être payée avant l'expédition.")
        
        # On passe par le service de livraison
        if hasattr(order, 'delivery'):
            DeliveryService.mark_as_ready(order.delivery.id, merchant_notes)
        
        order.status = Order.Status.SHIPPED
        order.save()
        return order

    @staticmethod
    @transaction.atomic
    def mark_as_delivered(order_id, otp_code=None):
        """
        Finalise la livraison (généralement appelé par le livreur via DeliveryService).
        """
        from delivery.services import DeliveryService
        order = Order.objects.select_related('delivery').get(id=order_id)
        
        if not hasattr(order, 'delivery'):
             # Fallback pour les commandes sans objet delivery (ne devrait pas arriver)
            order.status = Order.Status.DELIVERED
            order.save()
            return order

        # Si un code est fourni, on passe par la validation sécurisée
        if otp_code:
            DeliveryService.complete_delivery(order.delivery.id, otp_code)
        else:
            # Mode manuel/simple si pas de code (moins recommandé)
            order.status = Order.Status.DELIVERED
            order.save()
            
            delivery = order.delivery
            delivery.status = delivery.Status.DELIVERED
            delivery.delivered_at = timezone.now()
            delivery.save()
            
        return order


