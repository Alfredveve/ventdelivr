from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def product_list(request):
    """
    Liste tous les produits disponibles.
    """
    products = Product.objects.filter(is_available=True).select_related('merchant', 'category')
    categories = Category.objects.all()
    return render(request, 'catalog/product_list.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, slug):
    """
    Détail d'un produit avec options d'achat.
    """
    product = get_object_or_404(Product.objects.select_related('merchant', 'inventory'), slug=slug)
    # On récupère quelques produits recommandés (même catégorie)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'related_products': related_products
    })

def category_list(request):
    """
    Liste toutes les catégories disponibles.
    """
    categories = Category.objects.all()
    return render(request, 'catalog/category_list.html', {
        'categories': categories
    })

def category_detail(request, slug):
    """
    Affiche les produits d'une catégorie spécifique.
    """
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_available=True).select_related('merchant', 'inventory')
    
    return render(request, 'catalog/category_detail.html', {
        'category': category,
        'products': products
    })
