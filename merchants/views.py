from django.views.generic import DetailView
from .models import MerchantProfile
from catalog.models import Category

class MerchantDetailView(DetailView):
    model = MerchantProfile
    template_name = 'merchants/merchant_detail.html'
    context_object_name = 'merchant'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        merchant = self.object
        # Get products grouped by category
        context['categories'] = Category.objects.filter(
            products__merchant=merchant
        ).distinct()
        return context
