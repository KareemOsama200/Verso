from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from products.models import Product, ProductVariant
import uuid
import string
import random


def generate_order_number():
    """Generate unique order number"""
    prefix = 'VSO'  # Verso Store Order
    timestamp = timezone.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}{timestamp}{random_str}"


class Cart(models.Model):
    """Shopping cart"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart {self.session_key[:8]}"
    
    @property
    def total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        """Calculate cart subtotal"""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def tax(self):
        """Calculate tax (10% for demo)"""
        from decimal import Decimal
        return self.subtotal * Decimal('0.1')
    
    @property
    def shipping(self):
        """Calculate shipping (free over $50, else $5)"""
        from decimal import Decimal
        if self.subtotal >= 50:
            return Decimal('0')
        return Decimal('5')
    
    @property
    def total(self):
        """Calculate total price"""
        return self.subtotal + self.tax + self.shipping
    
    def clear(self):
        """Clear all items from cart"""
        self.items.all().delete()
    
    def merge_with(self, other_cart):
        """Merge another cart into this one"""
        for item in other_cart.items.all():
            existing = self.items.filter(
                product=item.product,
                variant=item.variant
            ).first()
            
            if existing:
                existing.quantity += item.quantity
                existing.save()
            else:
                item.cart = self
                item.save()
        
        other_cart.delete()


class CartItem(models.Model):
    """Items in shopping cart"""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-added_at']
        unique_together = ['cart', 'product', 'variant']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def unit_price(self):
        """Get unit price for item"""
        if self.variant:
            return self.variant.price
        return self.product.current_price
    
    @property
    def total_price(self):
        """Calculate total price for item"""
        return self.unit_price * self.quantity
    
    @property
    def is_available(self):
        """Check if item is available in requested quantity"""
        if self.variant:
            return self.variant.stock >= self.quantity
        return self.product.total_stock >= self.quantity


class Order(models.Model):
    """Customer orders"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('wallet', 'Store Wallet'),
        ('stripe', 'Credit/Debit Card (Stripe)'),
        ('paypal', 'PayPal'),
        ('test', 'Test Payment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    
    # Customer information (snapshot at time of order)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    # Shipping address (snapshot at time of order)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_country = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    shipping_longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Billing address (if different)
    billing_same_as_shipping = models.BooleanField(default=True)
    billing_address = models.TextField(blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    
    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('succeeded', 'Succeeded'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Payment details
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    paypal_order_id = models.CharField(max_length=255, blank=True)
    
    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True)
    carrier = models.CharField(max_length=50, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    
    # Notes
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = generate_order_number()
        
        # Update status timestamps
        if self.status == 'paid' and not self.paid_at:
            self.paid_at = timezone.now()
        elif self.status == 'shipped' and not self.shipped_at:
            self.shipped_at = timezone.now()
        elif self.status == 'delivered' and not self.delivered_at:
            self.delivered_at = timezone.now()
        elif self.status == 'cancelled' and not self.cancelled_at:
            self.cancelled_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Recalculate order totals from items"""
        from decimal import Decimal
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.tax = self.subtotal * Decimal('0.1')  # 10% tax
        if self.subtotal >= 50:
            self.shipping = Decimal('0')
        else:
            self.shipping = Decimal('5')
        self.total = self.subtotal + self.tax + self.shipping - self.discount
        self.save()
    
    def can_cancel(self):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'processing', 'paid']
    
    def can_refund(self):
        """Check if order can be refunded"""
        return self.status in ['paid', 'shipped', 'delivered']


class OrderItem(models.Model):
    """Items in an order"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Snapshot of product info at time of order
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50)
    size = models.CharField(max_length=10, blank=True)
    color = models.CharField(max_length=50, blank=True)
    
    # Pricing
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name}"
    
    @property
    def total_price(self):
        """Calculate total price for item"""
        return (self.unit_price * self.quantity) - self.discount_amount


class Transaction(models.Model):
    """Payment transactions"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('partial_refund', 'Partial Refund'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('succeeded', 'Succeeded'),
            ('failed', 'Failed'),
        ]
    )
    
    # External references
    stripe_charge_id = models.CharField(max_length=255, blank=True)
    paypal_transaction_id = models.CharField(max_length=255, blank=True)
    
    # Additional info
    response_data = models.JSONField(default=dict, blank=True)
    failure_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} - {self.status}"


class Coupon(models.Model):
    """Discount coupons"""
    
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Conditions
    minimum_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usage_limit = models.IntegerField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    single_use = models.BooleanField(default=False)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Restrictions
    applicable_categories = models.ManyToManyField('products.Category', blank=True)
    applicable_products = models.ManyToManyField('products.Product', blank=True)
    applicable_users = models.ManyToManyField(User, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.code
    
    def is_valid(self):
        """Check if coupon is currently valid"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from > now or self.valid_to < now:
            return False
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        return True
    
    def calculate_discount(self, subtotal):
        """Calculate discount amount for given subtotal"""
        if subtotal < self.minimum_purchase:
            return 0
        
        if self.discount_type == 'percentage':
            return subtotal * (self.discount_value / 100)
        else:
            return min(self.discount_value, subtotal)