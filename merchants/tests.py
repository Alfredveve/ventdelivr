from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import MerchantProfile
from .services import MerchantService
from catalog.services import ProductService
from catalog.models import Category, Product
from orders.models import Order, OrderItem

User = get_user_model()

class MerchantServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='merchant', password='password')
        self.merchant = MerchantProfile.objects.create(
            user=self.user, 
            store_name='Test Store'
        )
        self.category = Category.objects.create(name='Electronics')
        
    def test_product_lifecycle(self):
        """Test creating and updating a product via ProductService"""
        data = {
            'category': self.category.id,
            'name': 'Test Product',
            'price': 100.00,
            'description': 'A test product'
        }
        
        # Create
        product = ProductService.create_product(self.merchant, data)
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.merchant, self.merchant)
        
        # Update
        update_data = {'price': 120.00}
        updated_product = ProductService.update_product(product, update_data)
        self.assertEqual(updated_product.price, 120.00)

    def test_dashboard_stats(self):
        """Test dashboard stats calculation"""
        # Create product
        product = Product.objects.create(
            merchant=self.merchant,
            category=self.category,
            name='Stats Product',
            price=50.00
        )
        
        # Create Order
        user2 = User.objects.create_user(username='customer', password='password')
        order = Order.objects.create(
            customer=user2,
            total_price=100.00,
            status=Order.Status.PENDING
        )
        
        # Create OrderItem (2 items * 50.00 = 100.00)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            price=50.00
        )
        
        # Get Stats
        stats = MerchantService.get_dashboard_stats(self.merchant)
        
        self.assertEqual(stats['total_products'], 1)
        self.assertEqual(stats['total_orders'], 1)
        self.assertEqual(stats['total_sales'], 100.00)
        self.assertEqual(stats['pending_orders'], 1)
        
        # Mark order paid
        order.status = Order.Status.PAID
        order.save()
        
        stats_paid = MerchantService.get_dashboard_stats(self.merchant)
        self.assertEqual(stats_paid['pending_orders'], 0)
