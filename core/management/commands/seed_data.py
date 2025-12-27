from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from merchants.models import MerchantProfile
from catalog.models import Category, Product

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial merchants and products'

    def handle(self, *args, **options):
        # Create a superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' created"))

        # Create Merchant Users
        merchants_data = [
            {'username': 'mama_africa', 'store_name': 'Mama Africa Kitchen', 'address': '123 Montreal St, Canada'},
            {'username': 'lagos_bites', 'store_name': 'Lagos Bites', 'address': '456 Toronto Ave, Canada'},
            {'username': 'savannah_spices', 'store_name': 'Savannah Spices', 'address': '789 Ottawa Blvd, Canada'},
        ]

        for data in merchants_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={'role': User.Role.MERCHANT, 'email': f"{data['username']}@example.com"}
            )
            if created:
                user.set_password('pass123')
                user.save()
                MerchantProfile.objects.create(
                    user=user,
                    store_name=data['store_name'],
                    address=data['address'],
                    description=f"Authentic {data['store_name']} flavors right here in Canada."
                )
                self.stdout.write(self.style.SUCCESS(f"Merchant {data['store_name']} created"))

        # Create Categories
        categories_names = ['Main Dishes', 'Sides', 'Grocery Items', 'Spices']
        categories_objs = {}
        for name in categories_names:
            cat, created = Category.objects.get_or_create(name=name)
            categories_objs[name] = cat
            self.stdout.write(self.style.SUCCESS(f"Category {name} created"))

        # Create Products for Mama Africa
        mama_profile = MerchantProfile.objects.get(store_name='Mama Africa Kitchen')
        Product.objects.get_or_create(
            merchant=mama_profile,
            category=categories_objs['Main Dishes'],
            name='Jollof Rice with Grilled Chicken',
            defaults={'price': 18.50, 'description': 'Smoky West African classic served with spicy chicken.'}
        )
        Product.objects.get_or_create(
            merchant=mama_profile,
            category=categories_objs['Sides'],
            name='Fried Plantain (Alloco)',
            defaults={'price': 5.00, 'description': 'Sweet, ripe fried plantains.'}
        )

        self.stdout.write(self.style.SUCCESS("Data seeding complete!"))
