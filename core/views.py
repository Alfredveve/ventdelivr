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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Add specific context based on role
            user = self.request.user
            context['role'] = user.role
            if user.role == user.Role.MERCHANT:
                # Add merchant specific data if needed, e.g., order count
                pass
            elif user.role == user.Role.CUSTOMER:
                # Add customer specific data
                pass
        return context
