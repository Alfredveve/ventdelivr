from django.db import transaction
from .models import MerchantProfile

class MerchantService:
    """
    Service gérant la logique métier liée aux marchands.
    """
    
    @staticmethod
    @transaction.atomic
    def verify_merchant(merchant_profile_id, admin_user):
        """
        Valide un marchand (action réservée aux administrateurs).
        """
        if not admin_user.is_staff:
            raise PermissionError("Seuls les administrateurs peuvent valider un marchand.")
            
        profile = MerchantProfile.objects.get(id=merchant_profile_id)
        profile.is_verified = True
        profile.save()
        
        # On pourrait déclencher une notification ici
        return profile

    @staticmethod
    def update_store_info(profile, store_name, description, address):
        """
        Met à jour les informations de la boutique.
        """
        profile.store_name = store_name
        profile.description = description
        profile.address = address
        # Le slug sera mis à jour automatiquement par le modèle .save()
        profile.save()
        return profile

    @staticmethod
    def get_dashboard_stats(merchant_profile):
        """
        Récupère les statistiques pour le tableau de bord du marchand.
        """
        from orders.models import OrderItem, Order
        from django.db.models import Sum, F

        products = merchant_profile.products.all()
        
        # Commandes contenant au moins un produit du marchand
        order_items = OrderItem.objects.filter(product__merchant=merchant_profile)
        
        total_orders = order_items.values('order').distinct().count()
        
        # Calcul du revenu total
        # On suppose que OrderItem a les champs quantity et price
        revenue_data = order_items.aggregate(
            total_revenue=Sum(F('quantity') * F('price'))
        )
        total_revenue = revenue_data['total_revenue'] or 0

        pending_orders = order_items.filter(
            order__status=Order.Status.PENDING
        ).values('order').distinct().count()

        return {
            'total_products': products.count(),
            'total_orders': total_orders,
            'total_sales': total_revenue,
            'pending_orders': pending_orders,
        }

    @staticmethod
    def get_merchant_products(merchant_profile):
        """
        Récupère tous les produits du marchand.
        """
        return merchant_profile.products.all().select_related('category').order_by('-created_at')

    @staticmethod
    def get_recent_orders(merchant_profile, limit=5):
        """
        Récupère les commandes récentes pour ce marchand.
        """
        from orders.models import OrderItem
        
        return OrderItem.objects.filter(
            product__merchant=merchant_profile
        ).select_related('order', 'product').order_by('-order__created_at')[:limit]
