from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from products.models import Category, Brand, Product, ProductVariant, ProductImage, Tag
from orders.models import Order, OrderItem, Cart, CartItem
from accounts.models import CustomerProfile
from decimal import Decimal
import random
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with sample data'
    
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Seeding database with sample data...')
        
        # Create categories
        self.stdout.write('Creating categories...')
        categories = self.create_categories()
        
        # Create brands
        self.stdout.write('Creating brands...')
        brands = self.create_brands()
        
        # Create tags
        self.stdout.write('Creating tags...')
        tags = self.create_tags()
        
        # Create products
        self.stdout.write('Creating products...')
        products = self.create_products(categories, brands, tags)
        
        # Create staff users
        self.stdout.write('Creating staff users...')
        staff_users = self.create_staff_users()
        
        # Create customers
        self.stdout.write('Creating customers...')
        customers = self.create_customers()
        
        # Create sample orders
        self.stdout.write('Creating sample orders...')
        self.create_orders(customers, products)
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
    
    def create_categories(self):
        categories = []
        
        # Main categories
        men = Category.objects.create(
            name='Men',
            description='Men\'s clothing and accessories',
            display_order=1
        )
        categories.append(men)
        
        women = Category.objects.create(
            name='Women',
            description='Women\'s clothing and accessories',
            display_order=2
        )
        categories.append(women)
        
        # Subcategories for Men
        Category.objects.create(
            name='T-Shirts',
            parent=men,
            description='Men\'s t-shirts and casual tops',
            display_order=1
        )
        
        Category.objects.create(
            name='Jeans',
            parent=men,
            description='Men\'s denim and jeans',
            display_order=2
        )
        
        Category.objects.create(
            name='Jackets',
            parent=men,
            description='Men\'s jackets and outerwear',
            display_order=3
        )
        
        # Subcategories for Women
        Category.objects.create(
            name='Dresses',
            parent=women,
            description='Women\'s dresses',
            display_order=1
        )
        
        Category.objects.create(
            name='Tops',
            parent=women,
            description='Women\'s tops and blouses',
            display_order=2
        )
        
        Category.objects.create(
            name='Skirts',
            parent=women,
            description='Women\'s skirts',
            display_order=3
        )
        
        return categories
    
    def create_brands(self):
        brands = []
        
        brand_names = ['Urban Style', 'Verso Originals', 'Luxe Fashion', 'Street Wear Co.', 'Eco Threads']
        
        for name in brand_names:
            brand = Brand.objects.create(
                name=name,
                description=f'{name} - Premium quality fashion brand'
            )
            brands.append(brand)
        
        return brands
    
    def create_tags(self):
        tags = []
        tag_names = ['new-arrival', 'bestseller', 'summer', 'winter', 'casual', 'formal', 'eco-friendly', 'premium']
        
        for name in tag_names:
            tag = Tag.objects.create(name=name)
            tags.append(tag)
        
        return tags
    
    def create_products(self, categories, brands, tags):
        products = []
        
        # Product data
        product_data = [
            {
                'name': 'Classic White T-Shirt',
                'sku': 'TS-WHITE-001',
                'description': 'A timeless white t-shirt made from 100% organic cotton. Perfect for any casual occasion.',
                'short_description': 'Classic white tee in organic cotton',
                'base_price': Decimal('29.99'),
                'discount_percentage': Decimal('10'),
                'category': Category.objects.filter(name='T-Shirts').first(),
                'brand': brands[0],
                'gender': 'male',
                'material': '100% Organic Cotton',
                'care_instructions': 'Machine wash cold, tumble dry low',
                'features': ['Organic cotton', 'Regular fit', 'Crew neck', 'Short sleeves'],
                'sizes': ['S', 'M', 'L', 'XL'],
                'colors': [
                    {'name': 'White', 'hex': '#FFFFFF'},
                    {'name': 'Black', 'hex': '#000000'}
                ]
            },
            {
                'name': 'Floral Summer Dress',
                'sku': 'DR-FLORAL-002',
                'description': 'Beautiful floral print dress perfect for summer days. Features a flowing silhouette and comfortable fit.',
                'short_description': 'Elegant floral dress for summer',
                'base_price': Decimal('89.99'),
                'discount_percentage': Decimal('15'),
                'category': Category.objects.filter(name='Dresses').first(),
                'brand': brands[2],
                'gender': 'female',
                'material': 'Polyester blend',
                'care_instructions': 'Dry clean recommended',
                'features': ['Floral print', 'Midi length', 'V-neck', 'Sleeveless'],
                'sizes': ['XS', 'S', 'M', 'L'],
                'colors': [
                    {'name': 'Blue Floral', 'hex': '#4A90E2'},
                    {'name': 'Pink Floral', 'hex': '#FF69B4'}
                ]
            },
            {
                'name': 'Denim Slim Fit Jeans',
                'sku': 'JN-SLIM-003',
                'description': 'Modern slim fit jeans crafted from premium denim. Comfortable stretch fabric for all-day wear.',
                'short_description': 'Premium slim fit denim jeans',
                'base_price': Decimal('79.99'),
                'category': Category.objects.filter(name='Jeans').first(),
                'brand': brands[1],
                'gender': 'male',
                'material': '98% Cotton, 2% Elastane',
                'care_instructions': 'Machine wash cold, hang dry',
                'features': ['Slim fit', 'Stretch denim', '5-pocket design', 'Button fly'],
                'sizes': ['28', '30', '32', '34', '36'],
                'colors': [
                    {'name': 'Dark Blue', 'hex': '#1E3A5F'},
                    {'name': 'Light Blue', 'hex': '#87CEEB'}
                ]
            },
            {
                'name': 'Leather Biker Jacket',
                'sku': 'JK-LEATHER-004',
                'description': 'Classic leather biker jacket with modern styling. Premium quality leather with quilted lining.',
                'short_description': 'Premium leather biker jacket',
                'base_price': Decimal('299.99'),
                'discount_percentage': Decimal('20'),
                'category': Category.objects.filter(name='Jackets').first(),
                'brand': brands[3],
                'gender': 'unisex',
                'material': 'Genuine Leather',
                'care_instructions': 'Professional leather cleaning',
                'features': ['Genuine leather', 'Quilted lining', 'Multiple pockets', 'YKK zippers'],
                'sizes': ['S', 'M', 'L', 'XL'],
                'colors': [
                    {'name': 'Black', 'hex': '#000000'},
                    {'name': 'Brown', 'hex': '#8B4513'}
                ]
            },
            {
                'name': 'Silk Blouse',
                'sku': 'BL-SILK-005',
                'description': 'Elegant silk blouse perfect for both office and evening wear. Luxurious feel with a modern cut.',
                'short_description': 'Elegant silk blouse',
                'base_price': Decimal('119.99'),
                'category': Category.objects.filter(name='Tops').first(),
                'brand': brands[2],
                'gender': 'female',
                'material': '100% Silk',
                'care_instructions': 'Dry clean only',
                'features': ['Pure silk', 'Button-up front', 'Long sleeves', 'Relaxed fit'],
                'sizes': ['XS', 'S', 'M', 'L', 'XL'],
                'colors': [
                    {'name': 'Ivory', 'hex': '#FFFFF0'},
                    {'name': 'Navy', 'hex': '#000080'},
                    {'name': 'Burgundy', 'hex': '#800020'}
                ]
            }
        ]
        
        for data in product_data:
            # Create product
            sizes = data.pop('sizes')
            colors = data.pop('colors')
            
            product = Product.objects.create(**data)
            
            # Add tags
            random_tags = random.sample(tags, k=random.randint(2, 4))
            product.tags.set(random_tags)
            
            # Create variants
            for size in sizes:
                for color_info in colors:
                    # Map numeric sizes to CUSTOM or use standard sizes
                    if size in ['XS', 'S', 'M', 'L', 'XL', 'XXL']:
                        size_value = size
                        variant_color = color_info['name']
                    else:
                        # For numeric sizes like '28', '30' etc, use CUSTOM
                        size_value = 'CUSTOM'
                        # Create unique variant by appending size to color name
                        variant_color = f"{color_info['name']} (Size {size})"
                    
                    ProductVariant.objects.create(
                        product=product,
                        size=size_value,
                        color=variant_color,
                        color_hex=color_info['hex'],
                        stock=random.randint(5, 50),
                        sku_suffix=f"{size}-{color_info['name'][:3].upper()}"
                    )
            
            # Update total stock
            product.total_stock = sum(v.stock for v in product.variants.all())
            product.save()
            
            products.append(product)
        
        return products
    
    def create_staff_users(self):
        staff_users = []
        
        # Create manager
        manager = User.objects.create_user(
            username='manager',
            email='manager@verso-store.com',
            password='manager123',
            role='manager',
            first_name='John',
            last_name='Manager',
            phone_number='+1234567890',
            email_verified=True
        )
        staff_users.append(manager)
        
        # Create employee
        employee = User.objects.create_user(
            username='employee',
            email='employee@verso-store.com',
            password='employee123',
            role='employee',
            first_name='Jane',
            last_name='Employee',
            phone_number='+1234567891',
            email_verified=True
        )
        staff_users.append(employee)
        
        return staff_users
    
    def create_customers(self):
        customers = []
        
        customer_data = [
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'password': 'customer123',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone_number': '+1234567892',
                'address': '123 Main St',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA',
                'postal_code': '10001',
                'latitude': Decimal('40.7128'),
                'longitude': Decimal('-74.0060')
            },
            {
                'username': 'jane_smith',
                'email': 'jane@example.com',
                'password': 'customer123',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone_number': '+1234567893',
                'address': '456 Oak Ave',
                'city': 'Los Angeles',
                'state': 'CA',
                'country': 'USA',
                'postal_code': '90001',
                'latitude': Decimal('34.0522'),
                'longitude': Decimal('-118.2437')
            },
            {
                'username': 'bob_wilson',
                'email': 'bob@example.com',
                'password': 'customer123',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'phone_number': '+1234567894',
                'address': '789 Pine St',
                'city': 'Chicago',
                'state': 'IL',
                'country': 'USA',
                'postal_code': '60601',
                'latitude': Decimal('41.8781'),
                'longitude': Decimal('-87.6298')
            }
        ]
        
        for data in customer_data:
            customer = User.objects.create_user(**data)
            customer.email_verified = True
            customer.save()
            
            # Create customer profile
            CustomerProfile.objects.create(
                user=customer,
                newsletter_subscription=True,
                loyalty_points=random.randint(0, 500)
            )
            
            customers.append(customer)
        
        return customers
    
    def create_orders(self, customers, products):
        order_statuses = ['pending', 'processing', 'paid', 'shipped', 'delivered']
        payment_methods = ['cod', 'wallet', 'test']
        
        for customer in customers[:2]:  # Create orders for first two customers
            # Create 1-2 orders per customer
            for _ in range(random.randint(1, 2)):
                order = Order.objects.create(
                    user=customer,
                    customer_name=customer.full_name,
                    customer_email=customer.email,
                    customer_phone=customer.phone_number,
                    shipping_address=customer.address,
                    shipping_city=customer.city,
                    shipping_state=customer.state,
                    shipping_country=customer.country,
                    shipping_postal_code=customer.postal_code,
                    shipping_latitude=customer.latitude,
                    shipping_longitude=customer.longitude,
                    status=random.choice(order_statuses),
                    payment_method=random.choice(payment_methods),
                    subtotal=Decimal('0'),
                    tax=Decimal('0'),
                    shipping=Decimal('0'),
                    total=Decimal('0')
                )
                
                # Add 1-3 items to order
                order_products = random.sample(products, k=random.randint(1, 3))
                for product in order_products:
                    variant = product.variants.filter(stock__gt=0).first()
                    if variant:
                        quantity = random.randint(1, 2)
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            variant=variant,
                            product_name=product.name,
                            product_sku=product.sku,
                            size=variant.size,
                            color=variant.color,
                            unit_price=product.current_price,
                            quantity=quantity
                        )
                
                # Calculate totals
                order.calculate_totals()
                
                # Update created_at to vary dates
                order.created_at = timezone.now() - timedelta(days=random.randint(0, 30))
                order.save()