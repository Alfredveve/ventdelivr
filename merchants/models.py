from django.conf import settings
from django.db import models
from django.utils.text import slugify

class MerchantProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='merchant_profile'
    )
    store_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='merchants/logos/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='merchants/banners/', blank=True, null=True)
    address = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.store_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.store_name

    class Meta:
        verbose_name = "Merchant Profile"
        verbose_name_plural = "Merchant Profiles"
