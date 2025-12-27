from django.views.generic import DetailView, TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from .models import MerchantProfile
from .services import MerchantService
from catalog.models import Category, Product
from catalog.forms import ProductForm
from catalog.services import ProductService

class MerchantDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'merchants/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'merchant_profile'):
            merchant = self.request.user.merchant_profile
            context['merchant'] = merchant
            context['stats'] = MerchantService.get_dashboard_stats(merchant)
            context['recent_orders'] = MerchantService.get_recent_orders(merchant)
        return context

class MerchantProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'merchants/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        if hasattr(self.request.user, 'merchant_profile'):
            return MerchantService.get_merchant_products(self.request.user.merchant_profile)
        return Product.objects.none()

class MerchantProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'merchants/product_form.html'
    success_url = reverse_lazy('merchants:product_list')

    def form_valid(self, form):
        if hasattr(self.request.user, 'merchant_profile'):
            ProductService.create_product(self.request.user.merchant_profile, form.cleaned_data)
            return redirect(self.success_url)
        return super().form_valid(form)

class MerchantProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'merchants/product_form.html'
    success_url = reverse_lazy('merchants:product_list')

    def get_queryset(self):
        # Ensure merchants can only edit their own products
        if hasattr(self.request.user, 'merchant_profile'):
            return Product.objects.filter(merchant=self.request.user.merchant_profile)
        return Product.objects.none()

    def form_valid(self, form):
        ProductService.update_product(self.object, form.cleaned_data)
        return redirect(self.success_url)

class MerchantDetailView(DetailView):
    model = MerchantProfile
    template_name = 'merchants/merchant_detail.html'
    context_object_name = 'merchant'
    slug_url_kwarg = 'slug'

    def get(self, request, *args, **kwargs):
        # Support pour les anciens liens utilisant l'ID
        slug = self.kwargs.get(self.slug_url_kwarg)
        if slug and slug.isdigit():
            merchant = get_object_or_404(MerchantProfile, id=int(slug))
            return redirect('merchants:detail', slug=merchant.slug)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        merchant = self.object
        # Get products grouped by category
        context['categories'] = Category.objects.filter(
            products__merchant=merchant
        ).distinct()
        return context
