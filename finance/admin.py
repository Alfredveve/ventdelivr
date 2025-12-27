from django.contrib import admin
from .models import Wallet, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'updated_at')
    search_fields = ('user__username', 'user__email')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'timestamp', 'order')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('wallet__user__username', 'order__id')
