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

class Transaction(models.Model):
    class Type(models.TextChoices):
        DEPOSIT = 'DEPOSIT', 'Deposit'
        WITHDRAWAL = 'WITHDRAWAL', 'Withdrawal'
        PAYMENT = 'PAYMENT', 'Payment'
        REFUND = 'REFUND', 'Refund'

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=Type.choices)
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} for {self.wallet.user.username}"
