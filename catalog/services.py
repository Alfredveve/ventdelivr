from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from .models import Product, Category, Inventory

class InsufficientStockError(ValidationError):
    """Exception levée quand le stock est insuffisant."""
    pass

class ProductService:
    """
    Service gérant la logique métier liée aux produits.
    """

    @staticmethod
    @transaction.atomic
    def create_product(merchant_profile, data):
        """
        Crée un nouveau produit pour un marchand.
        """
        category_id = data.get('category')
        category = None
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                raise ValidationError({"category": "La catégorie sélectionnée n'existe pas."})

        product = Product(
            merchant=merchant_profile,
            category=category,
            name=data.get('name'),
            description=data.get('description', ''),
            price=data.get('price'),
            discount_price=data.get('discount_price'),
            image=data.get('image'),
            sku=data.get('sku'),
            weight=data.get('weight', 0.0),
            dimensions=data.get('dimensions', ''),
            is_available=data.get('is_available', True)
        )
        product.save()

        # Create initial inventory
        initial_stock = data.get('initial_stock', 0)
        low_stock_threshold = data.get('low_stock_threshold', 10)
        Inventory.objects.create(
            product=product,
            quantity=initial_stock,
            low_stock_threshold=low_stock_threshold
        )
        
        return product

    @staticmethod
    @transaction.atomic
    def update_product(product, data):
        """
        Met à jour un produit existant.
        """
        if 'category' in data:
            category_id = data.get('category')
            if category_id:
                try:
                    product.category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    raise ValidationError({"category": "La catégorie sélectionnée n'existe pas."})
            else:
                product.category = None
        
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'discount_price' in data:
            product.discount_price = data['discount_price']
        if 'image' in data:
            product.image = data['image']
        if 'is_available' in data:
            product.is_available = data['is_available']
        if 'sku' in data:
            product.sku = data['sku']
        if 'weight' in data:
            product.weight = data['weight']
        if 'dimensions' in data:
            product.dimensions = data['dimensions']
            
        product.save()
        return product

    @staticmethod
    def delete_product(product):
        """
        Supprime un produit (ou le marque comme archivé si nécessaire).
        """
        product.delete()

class InventoryService:
    """
    Service pour la gestion des stocks.
    """
    
    @staticmethod
    @transaction.atomic
    def adjust_stock(product, quantity, reason=None):
        """
        Ajuste le stock d'un produit. 
        `quantity` peut être positif (ajout) ou négatif (retrait).
        """
        inventory = product.inventory # Access via related_name
        
        new_quantity = inventory.quantity + quantity
        
        if new_quantity < 0:
            raise InsufficientStockError(f"Stock insuffisant pour {product.name}. Disponible: {inventory.quantity}")
            
        inventory.quantity = new_quantity
        inventory.save()
        return inventory

    @staticmethod
    def set_stock(product, quantity):
        """
        Définit le stock absolu.
        """
        if quantity < 0:
            raise ValidationError("La quantité ne peut pas être négative.")
            
        inventory = product.inventory
        inventory.quantity = quantity
        inventory.save()
        return inventory
