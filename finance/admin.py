from django.contrib import admin
from .models import Wallet, Transaction, Commission

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate', 'is_active', 'created_at')
    list_editable = ('rate', 'is_active')

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('updated_at',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'wallet', 'transaction_type', 'amount', 'status', 'label', 'timestamp')
    list_filter = ('transaction_type', 'status', 'label', 'timestamp')
    search_fields = ('reference', 'wallet__user__username', 'order__id', 'description')
    readonly_fields = ('reference', 'timestamp')
