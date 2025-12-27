from django.db import transaction
from django.db.models import F
from .models import Wallet, Transaction, Commission
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class InsufficientFundsError(ValueError):
    """Exception levée quand le solde est insuffisant."""
    pass

class FinanceService:
    """
    Service gérant les opérations financières selon les règles de l'art.
    """
    
    @staticmethod
    def get_active_commission_rate():
        """Récupère le taux de commission actif."""
        commission = Commission.objects.filter(is_active=True).first()
        return commission.rate if commission else Decimal('0.00')

    @staticmethod
    @transaction.atomic
    def transfer_funds(source_wallet, destination_wallet, amount, label, transaction_type=Transaction.Type.TRANSFER, order=None, description=""):
        """
        Déplace l'argent entre deux portefeuilles avec verrouillage au niveau de la ligne.
        """
        if amount <= 0:
            raise ValueError("Le montant doit être supérieur à zéro.")

        # Verrouiller les deux portefeuilles pour éviter les conditions de course
        # On utilise select_for_update() sur les IDs pour garantir l'ordre et éviter les deadlocks
        wallet_ids = sorted([source_wallet.id, destination_wallet.id])
        wallets = Wallet.objects.select_for_update().filter(id__in=wallet_ids)
        
        # Récupérer les instances verrouillées
        locked_source = (wallets.get(id=source_wallet.id) if source_wallet else None)
        locked_dest = wallets.get(id=destination_wallet.id)

        if locked_source:
            if locked_source.balance < amount:
                raise InsufficientFundsError(f"Solde insuffisant : {locked_source.balance} < {amount}")
            
            locked_source.balance = F('balance') - amount
            locked_source.save()
            
            Transaction.objects.create(
                wallet=locked_source,
                amount=-amount,
                transaction_type=transaction_type,
                label=label,
                order=order,
                description=description,
                status=Transaction.Status.COMPLETED
            )

        locked_dest.balance = F('balance') + amount
        locked_dest.save()

        Transaction.objects.create(
            wallet=locked_dest,
            amount=amount,
            transaction_type=transaction_type,
            label=label,
            order=order,
            description=description,
            status=Transaction.Status.COMPLETED
        )
        
        return True

    @staticmethod
    @transaction.atomic
    def process_order_payment(order):
        """
        Gère le paiement d'une commande par le client.
        L'argent est débité du client. On pourrait le mettre en 'séquestre' 
        ou simplement marquer la commande comme payée.
        """
        customer_wallet = order.customer.wallet
        # On verrouille le portefeuille client
        customer_wallet = Wallet.objects.select_for_update().get(id=customer_wallet.id)
        
        if customer_wallet.balance < order.total_price:
            raise InsufficientFundsError("Solde insuffisant pour payer la commande.")
            
        customer_wallet.balance -= order.total_price
        customer_wallet.save()
        
        Transaction.objects.create(
            wallet=customer_wallet,
            amount=-order.total_price,
            transaction_type=Transaction.Type.PAYMENT,
            label=Transaction.Label.ORDER_PAYMENT,
            order=order,
            description=f"Paiement de la commande #{order.id}",
            status=Transaction.Status.COMPLETED
        )
        
        # Note: L'argent reste "dans le système" jusqu'à la livraison
        return True

    @staticmethod
    @transaction.atomic
    def settle_merchant_payout(order):
        """
        Verse les fonds aux marchands après livraison, déduction faite de la commission.
        Gère les commandes multi-marchands en ventilant les paiements par article.
        """
        commission_rate = FinanceService.get_active_commission_rate()
        
        # On regroupe par marchand pour minimiser les transactions
        merchant_shares = {}
        
        for item in order.items.select_related('product__merchant__user__wallet').all():
            merchant = item.product.merchant
            if merchant not in merchant_shares:
                merchant_shares[merchant] = Decimal('0.00')
            merchant_shares[merchant] += item.price * item.quantity

        for merchant, total_share in merchant_shares.items():
            if not hasattr(merchant.user, 'wallet'):
                logger.error(f"Portefeuille manquant pour le marchand {merchant.store_name}")
                continue

            commission_amount = (total_share * commission_rate / 100).quantize(Decimal('0.01'))
            merchant_amount = total_share - commission_amount

            merchant_wallet = Wallet.objects.select_for_update().get(id=merchant.user.wallet.id)
            
            # Créditer le marchand
            merchant_wallet.balance = F('balance') + merchant_amount
            merchant_wallet.save()
            
            Transaction.objects.create(
                wallet=merchant_wallet,
                amount=merchant_amount,
                transaction_type=Transaction.Type.TRANSFER,
                label=Transaction.Label.MERCHANT_PAYOUT,
                order=order,
                description=f"Versement pour la commande #{order.id} ({merchant.store_name})",
                status=Transaction.Status.COMPLETED
            )

            # Enregistrer la commission plateforme (on pourrait créditer un PlatformWallet ici)
            Transaction.objects.create(
                wallet=merchant_wallet, # Trace associée au marchand pour cet exemple
                amount=commission_amount,
                transaction_type=Transaction.Type.TRANSFER,
                label=Transaction.Label.COMMISSION,
                order=order,
                description=f"Portion commission plateforme ({commission_rate}%) sur commande #{order.id}",
                status=Transaction.Status.COMPLETED
            )

        return True

    @staticmethod
    @transaction.atomic
    def deposit_funds(wallet, amount, description="Rechargement"):
        """Crédite le portefeuille."""
        wallet = Wallet.objects.select_for_update().get(id=wallet.id)
        wallet.balance = F('balance') + amount
        wallet.save()
        
        Transaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type=Transaction.Type.DEPOSIT,
            label=Transaction.Label.WALLET_DEPOSIT,
            description=description,
            status=Transaction.Status.COMPLETED
        )
        return wallet
