from django.views.generic import ListView
from merchants.models import MerchantProfile

class HomeView(ListView):
    model = MerchantProfile
    template_name = 'core/index.html'
    context_object_name = 'merchants'

    def get_queryset(self):
        queryset = MerchantProfile.objects.filter(is_verified=True)
        # For now, show all for demo purposes even if not verified in seed
        if not queryset.exists():
            queryset = MerchantProfile.objects.all()
        return queryset
