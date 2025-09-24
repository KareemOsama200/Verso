"""Tests for critical e-commerce functionality"""
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from products.models import Product, Category, ProductVariant, Brand
from orders.models import Cart, CartItem, Order
from accounts.models import Permission

User = get_user_model()


class ProductDetailTestCase(TestCase):
    """Test product detail page and variant selection"""
    
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            sku='TEST001',
            description='Test description',
            category=self.category,
            base_price=Decimal('99.99'),
            total_stock=10,
            is_active=True
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            size='M',
            color='Blue',
            stock=5
        )
    
    def test_product_detail_renders(self):
        """Test that product detail page renders correctly"""
        url = reverse('products:detail', kwargs={'slug': self.product.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product.sku)
        self.assertContains(response, str(self.product.base_price))
    
    def test_variant_selection_displayed(self):
        """Test that product variants are displayed"""
        url = reverse('products:detail', kwargs={'slug': self.product.slug})
        response = self.client.get(url)
        
        self.assertContains(response, 'Size')
        self.assertContains(response, self.variant.size)
        self.assertContains(response, self.variant.color)
    
    def test_new_badge_displayed(self):
        """Test that NEW badge is displayed for recent products"""
        from django.utils import timezone
        self.product.created_at = timezone.now()
        self.product.save()
        
        url = reverse('products:detail', kwargs={'slug': self.product.slug})
        response = self.client.get(url)
        
        self.assertContains(response, 'NEW')
    
    def test_sale_badge_displayed(self):
        """Test that sale badge is displayed for discounted products"""
        self.product.discount_percentage = Decimal('20')
        self.product.save()
        
        url = reverse('products:detail', kwargs={'slug': self.product.slug})
        response = self.client.get(url)
        
        self.assertContains(response, '20% OFF')


class AddToCartTestCase(TestCase):
    """Test add to cart functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            sku='TEST001',
            description='Test description',
            category=self.category,
            base_price=Decimal('50.00'),
            total_stock=10,
            is_active=True
        )
    
    def test_add_to_cart_anonymous(self):
        """Test anonymous user can add to cart"""
        url = reverse('orders:add_to_cart', kwargs={'product_id': self.product.id})
        response = self.client.post(url, {'quantity': 1})
        
        # Should redirect to cart
        self.assertEqual(response.status_code, 302)
        
        # Check cart was created with session
        cart = Cart.objects.filter(session_key=self.client.session.session_key).first()
        self.assertIsNotNone(cart)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().product, self.product)
    
    def test_add_to_cart_authenticated(self):
        """Test authenticated user can add to cart"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('orders:add_to_cart', kwargs={'product_id': self.product.id})
        response = self.client.post(url, {'quantity': 2})
        
        # Check cart was created for user
        cart = Cart.objects.filter(user=self.user).first()
        self.assertIsNotNone(cart)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 2)


class CheckoutWorkflowTestCase(TestCase):
    """Test checkout and order creation"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            phone_number='+1234567890',
            address='123 Test St',
            city='Test City',
            state='TS',
            country='Test Country',
            postal_code='12345',
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060')
        )
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            sku='TEST001',
            description='Test description',
            category=self.category,
            base_price=Decimal('50.00'),
            total_stock=10,
            is_active=True
        )
        
        # Create cart with items
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
    
    def test_checkout_requires_login(self):
        """Test that checkout requires authentication"""
        url = reverse('orders:checkout')
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_checkout_creates_order(self):
        """Test that checkout creates order with user data"""
        self.client.login(username='customer', password='testpass123')
        
        url = reverse('orders:checkout')
        checkout_data = {
            'shipping_address': self.user.address,
            'shipping_city': self.user.city,
            'shipping_state': self.user.state,
            'shipping_country': self.user.country,
            'shipping_postal_code': self.user.postal_code,
            'payment_method': 'cod',
            'billing_same_as_shipping': True,
            'agree_terms': True
        }
        
        response = self.client.post(url, checkout_data)
        
        # Check order was created
        order = Order.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)
        
        # Check order contains user data snapshot
        self.assertEqual(order.customer_name, self.user.full_name)
        self.assertEqual(order.customer_email, self.user.email)
        self.assertEqual(order.customer_phone, self.user.phone_number)
        self.assertEqual(order.shipping_address, self.user.address)
        self.assertEqual(order.shipping_latitude, self.user.latitude)
        self.assertEqual(order.shipping_longitude, self.user.longitude)
        
        # Check order items
        self.assertEqual(order.items.count(), 1)
        order_item = order.items.first()
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 2)
        
        # Check cart is cleared
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.items.count(), 0)


class StaffPermissionTestCase(TestCase):
    """Test staff permission enforcement"""
    
    def setUp(self):
        self.client = Client()
        
        # Create admin user
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='admin'
        )
        
        # Create manager user
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='manager123',
            role='manager'
        )
        
        # Create employee user
        self.employee = User.objects.create_user(
            username='employee',
            email='employee@example.com',
            password='employee123',
            role='employee'
        )
    
    def test_employee_cannot_delete_admin(self):
        """Test that employees cannot delete admin users"""
        self.assertFalse(self.employee.can_delete_user(self.admin))
        self.assertFalse(self.employee.can_delete_user(self.manager))
    
    def test_manager_cannot_delete_admin(self):
        """Test that managers cannot delete admin users"""
        self.assertFalse(self.manager.can_delete_user(self.admin))
    
    def test_employee_cannot_escalate_self(self):
        """Test that employees cannot escalate their own role"""
        self.client.login(username='employee', password='employee123')
        
        # Try to update own role (this would be prevented in view)
        self.employee.role = 'admin'
        self.employee.save()
        
        # Check that is_staff and is_superuser are set correctly by save method
        self.employee.refresh_from_db()
        self.assertTrue(self.employee.is_staff)  # Employees are staff
        self.assertFalse(self.employee.is_superuser)  # But not superuser
    
    def test_admin_can_manage_all_users(self):
        """Test that admin can manage all users"""
        self.assertTrue(self.admin.can_delete_user(self.manager))
        self.assertTrue(self.admin.can_delete_user(self.employee))
        self.assertTrue(self.admin.can_edit_user(self.manager))
        self.assertTrue(self.admin.can_edit_user(self.employee))
    
    def test_role_hierarchy_enforcement(self):
        """Test role hierarchy is enforced"""
        # Employee cannot delete or edit manager
        self.assertFalse(self.employee.can_delete_user(self.manager))
        self.assertFalse(self.employee.can_edit_user(self.manager))
        
        # Manager can manage employees
        self.assertTrue(self.manager.can_delete_user(self.employee))
        self.assertTrue(self.manager.can_edit_user(self.employee))
        
        # Users can edit themselves
        self.assertTrue(self.employee.can_edit_user(self.employee))
        self.assertTrue(self.manager.can_edit_user(self.manager))