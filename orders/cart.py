"""
Gestion du panier d'achat en session.
"""
from decimal import Decimal
from django.conf import settings
from catalog.models import Product


class Cart:
    """
    Classe pour gérer le panier d'achat stocké en session.
    """
    
    def __init__(self, request):
        """
        Initialise le panier.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Créer un nouveau panier vide
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def add(self, product, quantity=1, override_quantity=False):
        """
        Ajoute un produit au panier ou met à jour sa quantité.
        
        Args:
            product: Instance du produit
            quantity: Quantité à ajouter
            override_quantity: Si True, remplace la quantité au lieu de l'ajouter
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.discount_price if product.discount_price else product.price)
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        self.save()
    
    def save(self):
        """
        Marque la session comme modifiée pour forcer sa sauvegarde.
        """
        self.session.modified = True
    
    def remove(self, product):
        """
        Retire un produit du panier.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def update(self, product_id, quantity):
        """
        Met à jour la quantité d'un produit.
        """
        product_id = str(product_id)
        if product_id in self.cart:
            if quantity > 0:
                self.cart[product_id]['quantity'] = quantity
            else:
                del self.cart[product_id]
            self.save()
    
    def __iter__(self):
        """
        Itère sur les articles du panier et récupère les produits depuis la base.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
    
    def __len__(self):
        """
        Compte tous les articles dans le panier.
        """
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        """
        Calcule le prix total du panier.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
    
    def clear(self):
        """
        Vide le panier.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()
    
    def get_items_data(self):
        """
        Retourne les données du panier au format attendu par OrderService.
        """
        items = []
        for product_id, item_data in self.cart.items():
            items.append({
                'product_id': int(product_id),
                'quantity': item_data['quantity']
            })
        return items
