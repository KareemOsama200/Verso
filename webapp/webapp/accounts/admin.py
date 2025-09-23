from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Permission, CustomerProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        (_('Role & Permissions'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Address'), {'fields': ('address', 'city', 'state', 'country', 'postal_code', 'latitude', 'longitude')}),
        (_('Additional'), {'fields': ('profile_image', 'bio', 'wallet_balance', 'email_verified')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    
    list_display = ['username', 'email', 'full_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser', 'email_verified', 'created_at']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Admin for custom permissions"""
    
    list_display = ['user', 'permission', 'granted_by', 'granted_at']
    list_filter = ['permission', 'granted_at']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user', 'granted_by']
    readonly_fields = ['granted_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.granted_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    """Admin for customer profiles"""
    
    list_display = ['user', 'loyalty_tier', 'loyalty_points', 'total_orders', 'total_spent']
    list_filter = ['loyalty_tier', 'newsletter_subscription', 'sms_notifications']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']
    readonly_fields = ['total_orders', 'total_spent']