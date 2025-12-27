import uuid
from django.db import models
from django.conf import settings
from orders.models import Order
from decimal import Decimal

class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet of {self.user.username} - {self.balance}"

class Commission(models.Model):
    name = models.CharField(max_length=100, default="Platform Fee")
    rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage (e.g. 10.00 for 10%)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.name} ({self.rate}%) - {status}"

class Transaction(models.Model):
    class Type(models.TextChoices):
        DEPOSIT = 'DEPOSIT', 'Dépôt'
        WITHDRAWAL = 'WITHDRAWAL', 'Retrait'
        PAYMENT = 'PAYMENT', 'Paiement'
        REFUND = 'REFUND', 'Remboursement'
        TRANSFER = 'TRANSFER', 'Transfert'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        COMPLETED = 'COMPLETED', 'Terminé'
        FAILED = 'FAILED', 'Échoué'
        CANCELLED = 'CANCELLED', 'Annulé'

    class Label(models.TextChoices):
        ORDER_PAYMENT = 'ORDER_PAYMENT', 'Paiement de commande'
        MERCHANT_PAYOUT = 'MERCHANT_PAYOUT', 'Versement marchand'
        COMMISSION = 'COMMISSION', 'Commission plateforme'
        WALLET_DEPOSIT = 'WALLET_DEPOSIT', 'Rechargement portefeuille'
        MANUAL_ADJUSTMENT = 'MANUAL_ADJUSTMENT', 'Ajustement manuel'

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=Type.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.COMPLETED)
    label = models.CharField(max_length=50, choices=Label.choices, blank=True, null=True)
    
    reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    description = models.TextField(blank=True)
    
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='finance_transactions'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} ({self.amount}) - {self.wallet.user.username} - {self.status}"
