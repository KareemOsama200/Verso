from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import uuid


class User(AbstractUser):
    """Custom User model with role-based permissions"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
        ('customer', 'Customer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    email = models.EmailField(_('email address'), unique=True)
    
    # Customer specific fields
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Address fields
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Location fields for map
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Additional fields
    date_of_birth = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(blank=True)
    
    # Wallet
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Email verification
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def is_staff_member(self):
        return self.role in ['admin', 'manager', 'employee']
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_manager(self):
        return self.role == 'manager'
    
    @property
    def is_employee(self):
        return self.role == 'employee'
    
    @property
    def is_customer(self):
        return self.role == 'customer'
    
    def has_module_perms(self, app_label):
        """Override to use role-based permissions"""
        if self.is_superuser or self.is_admin:
            return True
        return super().has_module_perms(app_label)
    
    def has_perm(self, perm, obj=None):
        """Override to use role-based permissions"""
        if self.is_superuser or self.is_admin:
            return True
        
        # Define permission matrix
        permission_matrix = {
            'manager': [
                'products.add_product',
                'products.change_product',
                'products.view_product',
                'orders.view_order',
                'orders.change_order',
                'accounts.view_user',
                'accounts.add_user',  # Can add employees only
            ],
            'employee': [
                'products.view_product',
                'orders.view_order',
                'orders.change_order',
                'accounts.view_user',
            ],
            'customer': [
                'orders.add_order',
                'orders.view_order',  # Own orders only
            ]
        }
        
        if self.role in permission_matrix:
            return perm in permission_matrix[self.role]
        
        return super().has_perm(perm, obj)
    
    def can_delete_user(self, target_user):
        """Check if current user can delete target user"""
        if not self.is_staff_member:
            return False
        
        # Admins cannot be deleted by anyone except superuser
        if target_user.is_admin and not self.is_superuser:
            return False
        
        # Users cannot delete users with equal or higher role
        role_hierarchy = {'customer': 0, 'employee': 1, 'manager': 2, 'admin': 3}
        
        if role_hierarchy.get(target_user.role, 0) >= role_hierarchy.get(self.role, 0):
            return False
        
        return True
    
    def can_edit_user(self, target_user):
        """Check if current user can edit target user"""
        if not self.is_staff_member:
            return False
        
        # Users can edit themselves
        if self.id == target_user.id:
            return True
        
        # Apply same hierarchy as delete
        return self.can_delete_user(target_user)
    
    def save(self, *args, **kwargs):
        # Set is_staff based on role
        if self.role in ['admin', 'manager', 'employee']:
            self.is_staff = True
        else:
            self.is_staff = False
        
        # Set is_superuser for admin role
        if self.role == 'admin':
            self.is_superuser = True
        
        super().save(*args, **kwargs)


class Permission(models.Model):
    """Granular permissions for staff members"""
    
    PERMISSION_CHOICES = [
        ('can_create_product', 'Can Create Products'),
        ('can_edit_product', 'Can Edit Products'),
        ('can_delete_product', 'Can Delete Products'),
        ('can_view_orders', 'Can View Orders'),
        ('can_manage_orders', 'Can Manage Orders'),
        ('can_refund_orders', 'Can Refund Orders'),
        ('can_manage_staff', 'Can Manage Staff'),
        ('can_view_analytics', 'Can View Analytics'),
        ('can_manage_customers', 'Can Manage Customers'),
        ('can_export_data', 'Can Export Data'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_permissions')
    permission = models.CharField(max_length=50, choices=PERMISSION_CHOICES)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='permissions_granted')
    granted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'permission']
        ordering = ['user', 'permission']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_permission_display()}"


class CustomerProfile(models.Model):
    """Extended profile for customers"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    
    # Preferences
    newsletter_subscription = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Shopping preferences
    preferred_sizes = models.JSONField(default=list, blank=True)
    preferred_colors = models.JSONField(default=list, blank=True)
    preferred_categories = models.JSONField(default=list, blank=True)
    
    # Loyalty program
    loyalty_points = models.IntegerField(default=0)
    loyalty_tier = models.CharField(
        max_length=20,
        choices=[
            ('bronze', 'Bronze'),
            ('silver', 'Silver'),
            ('gold', 'Gold'),
            ('platinum', 'Platinum'),
        ],
        default='bronze'
    )
    
    # Statistics
    total_orders = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"Profile of {self.user.username}"