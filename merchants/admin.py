from django.contrib import admin
from .models import MerchantProfile

@admin.register(MerchantProfile)
class MerchantProfileAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'user', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('store_name', 'user__username', 'user__email')
    actions = ['verify_merchants']

    @admin.action(description='Vérifier les marchands sélectionnés')
    def verify_merchants(self, request, queryset):
        queryset.update(is_verified=True)
