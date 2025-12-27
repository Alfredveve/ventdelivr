from django.db import transaction
from .models import Wallet, Transaction

class FinanceService:
    """
    Service gérant les opérations financières.
    """
    
    @staticmethod
    @transaction.atomic
    def process_payment(customer_wallet, amount, order):
        """
        Débite le portefeuille du client pour une commande.
        """
        if customer_wallet.balance < amount:
            raise ValueError("Solde insuffisant.")
            
        customer_wallet.balance -= amount
        customer_wallet.save()
        
        Transaction.objects.create(
            wallet=customer_wallet,
            amount=-amount,
            transaction_type=Transaction.Type.PAYMENT,
            order=order
        )
        return True

    @staticmethod
    @transaction.atomic
    def deposit_funds(wallet, amount):
        """
        Crédite le portefeuille.
        """
        wallet.balance += amount
        wallet.save()
        
        Transaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type=Transaction.Type.DEPOSIT
        )
        return wallet
