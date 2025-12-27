from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer'
        MERCHANT = 'MERCHANT', 'Merchant'
        DRIVER = 'DRIVER', 'Driver'
        ADMIN = 'ADMIN', 'Admin'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
