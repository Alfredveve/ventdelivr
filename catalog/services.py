from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from .models import Product, Category

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
            is_available=data.get('is_available', True)
        )
        product.save()
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
            
        product.save()
        return product

    @staticmethod
    def delete_product(product):
        """
        Supprime un produit (ou le marque comme archivé si nécessaire).
        """
        product.delete()
