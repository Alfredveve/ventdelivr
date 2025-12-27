from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Order, OrderItem
from .services import OrderService
from .cart import Cart
from catalog.models import Product

def merchant_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != request.user.Role.MERCHANT:
            messages.error(request, "Accès réservé aux marchands.")
            return redirect('core:index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# ==================== CART VIEWS ====================

def cart_view(request):
    """
    Affiche le panier d'achat.
    """
    cart = Cart(request)
    return render(request, 'orders/cart.html', {'cart': cart})

@require_POST
def add_to_cart(request, product_id):
    """
    Ajoute un produit au panier.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    # Vérifier la disponibilité
    if not product.is_available:
        messages.error(request, f"{product.name} n'est plus disponible.")
        return redirect('catalog:product_detail', slug=product.slug)
    
    # Vérifier le stock
    if hasattr(product, 'inventory') and product.inventory.quantity < quantity:
        messages.error(request, f"Stock insuffisant pour {product.name}.")
        return redirect('catalog:product_detail', slug=product.slug)
    
    cart.add(product=product, quantity=quantity)
    messages.success(request, f"{product.name} a été ajouté au panier.")
    
    # Rediriger vers la page précédente ou le panier
    next_url = request.POST.get('next', 'orders:cart')
    return redirect(next_url)

@require_POST
def remove_from_cart(request, product_id):
    """
    Retire un produit du panier.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"{product.name} a été retiré du panier.")
    return redirect('orders:cart')

@require_POST
def update_cart(request):
    """
    Met à jour les quantités dans le panier.
    """
    cart = Cart(request)
    
    for key, value in request.POST.items():
        if key.startswith('quantity_'):
            product_id = key.split('_')[1]
            quantity = int(value)
            cart.update(product_id, quantity)
    
    messages.success(request, "Panier mis à jour.")
    return redirect('orders:cart')

@login_required
@require_POST
def checkout(request):
    """
    Valide le panier et crée une commande.
    """
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.error(request, "Votre panier est vide.")
        return redirect('orders:cart')
    
    try:
        # Créer la commande à partir du panier
        items_data = cart.get_items_data()
        order = OrderService.place_order(request.user, items_data)
        
        # Vider le panier
        cart.clear()
        
        messages.success(request, f"Commande #{order.id} créée avec succès ! Elle est en attente de paiement.")
        return redirect('orders:detail', order_id=order.id)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la création de la commande : {e}")
        return redirect('orders:cart')

# ==================== ORDER VIEWS ====================


@login_required
def order_list(request):
    """
    Historique des commandes du client.
    """
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'orders/list.html', {'orders': orders})

@login_required
@merchant_required
def merchant_orders(request):
    """
    Liste des commandes reçues par le marchand.
    """
    # On trouve les commandes qui contiennent au moins un produit de ce marchand
    orders = Order.objects.filter(
        items__product__merchant=request.user.merchant_profile
    ).distinct().order_by('-created_at')
    return render(request, 'orders/merchant_orders.html', {'orders': orders})

@login_required
@merchant_required
def ship_order(request, order_id):
    """
    Action pour expédier une commande.
    """
    if request.method == 'POST':
        try:
            OrderService.ship_order(order_id)
            messages.success(request, f"Commande #{order_id} marquée comme expédiée.")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'expédition : {e}")
    return redirect('orders:merchant_orders')

@login_required
def quick_buy(request, product_id):
    """
    Crée une commande instantanée pour un produit unique.
    """
    if request.method != 'POST':
        return redirect('catalog:product_list')
        
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        # On utilise le service pour placer la commande (avec réservation de stock)
        items_data = [{'product_id': product_id, 'quantity': quantity}]
        order = OrderService.place_order(request.user, items_data)
        
        messages.success(request, f"Commande #{order.id} créée avec succès ! Elle est en attente de paiement.")
        return redirect('orders:detail', order_id=order.id)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la création de la commande : {e}")
        return redirect('catalog:product_list')

@login_required
def deliver_order(request, order_id):
    """
    Action pour marquer comme livrée (utilisée par le livreur ou pour démo).
    """
    if request.method == 'POST':
        try:
            OrderService.mark_as_delivered(order_id)
            messages.success(request, f"Commande #{order_id} livrée avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la livraison : {e}")
            
    # Rediriger vers le détail (pour le client) ou la liste (pour démo)
    return redirect('orders:detail', order_id=order_id)


@login_required
def order_detail(request, order_id):
    """
    Affiche le détail d'une commande avec un design premium.
    """
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'orders/detail.html', {'order': order})

@login_required
def order_fulfill(request, order_id):
    """
    Traite le paiement de la commande via le OrderService.
    """
    if request.method != 'POST':
        return redirect('orders:detail', order_id=order_id)
        
    try:
        order = OrderService.fulfill_order(order_id)
        messages.success(request, f"Paiement réussi pour la commande #{order.id} !")
    except Exception as e:
        messages.error(request, f"Erreur lors du paiement : {e}")
        
    return redirect('orders:detail', order_id=order_id)

@login_required
def order_cancel(request, order_id):
    """
    Annule la commande et restaure les stocks.
    """
    if request.method != 'POST':
        return redirect('orders:detail', order_id=order_id)
        
    try:
        order = OrderService.cancel_order(order_id)
        messages.warning(request, f"La commande #{order.id} a été annulée.")
    except Exception as e:
        messages.error(request, f"Impossible d'annuler la commande : {e}")
        
    return redirect('orders:detail', order_id=order_id)
