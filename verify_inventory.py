import os
import django
import sys

# Setup Django environment
sys.path.append(r'c:\Users\codeshester0011\Desktop\proJetAB\ventdelivr')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ventdelivr.settings')
django.setup()

from django.contrib.auth import get_user_model
from merchants.models import MerchantProfile
from catalog.models import Category, Product, Inventory
from catalog.services import ProductService, InventoryService

User = get_user_model()

def verify():
    print("Starting verification...")
    
    # Clean up previous verification data
    Product.objects.filter(sku='TEST-SKU-001').delete()
    Category.objects.filter(slug='test-category').delete()
    User.objects.filter(username='testmerchant').delete()

    # 1. Create User and Merchant
    user = User.objects.create_user(username='testmerchant', password='password')
    merchant = MerchantProfile.objects.create(user=user, store_name="Test Store", address="123 Test St")
    print("Merchant created.")

    # 2. Create Category
    category = Category.objects.create(name="Test Category")
    print("Category created.")

    # 3. Create Product via Service
    data = {
        'name': 'Test Product',
        'category': category.id,
        'price': 100.00,
        'sku': 'TEST-SKU-001',
        'weight': 1.5,
        'initial_stock': 50,
        'low_stock_threshold': 5
    }
    
    product = ProductService.create_product(merchant, data)
    print(f"Product created: {product.name} (SKU: {product.sku})")

    # 4. Verify Inventory created
    try:
        inventory = product.inventory
        print(f"Inventory found: {inventory.quantity} units.")
        assert inventory.quantity == 50
    except Inventory.DoesNotExist:
        print("ERROR: Inventory not created!")
        return

    # 5. Adjust stock
    updated_inv = InventoryService.adjust_stock(product, -5, reason="Sale")
    print(f"Stock adjusted. New quantity: {updated_inv.quantity}")
    assert updated_inv.quantity == 45

    # 6. Verify low stock logic (optional, just checking model)
    updated_inv = InventoryService.set_stock(product, 4)
    print(f"Stock set to {updated_inv.quantity}. Low stock? {updated_inv.quantity < updated_inv.low_stock_threshold}")
    
    print("Verification Successful!")

if __name__ == '__main__':
    try:
        verify()
    except Exception as e:
        print(f"Verification FAILED: {e}")
