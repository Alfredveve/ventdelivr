import os
import django
import sys
import uuid

# Setup Django environment
sys.path.append(r'c:\Users\codeshester0011\Desktop\proJetAB\ventdelivr')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ventdelivr.settings')
django.setup()

from catalog.models import Product

def populate():
    products = Product.objects.filter(sku__isnull=True)
    count = 0
    for p in products:
        p.sku = f"SKU-{p.id}-{uuid.uuid4().hex[:8].upper()}"
        p.save()
        count += 1
    print(f"Updated {count} products with SKUs.")

if __name__ == '__main__':
    populate()
