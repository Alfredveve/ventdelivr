from django.contrib import admin
from .models import Category, Product, Inventory

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class InventoryInline(admin.StackedInline):
    model = Inventory
    can_delete = False
    verbose_name_plural = 'Inventory'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'merchant', 'price', 'sku', 'is_available', 'get_stock')
    list_filter = ('is_available', 'merchant', 'category')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [InventoryInline]

    def get_stock(self, obj):
        if hasattr(obj, 'inventory'):
            return obj.inventory.quantity
        return "N/A"
    get_stock.short_description = 'Stock'

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'low_stock_threshold', 'last_updated')
