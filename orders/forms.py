from django import forms
from .models import Order, Coupon
from accounts.forms import AddressForm


class CheckoutForm(AddressForm):
    """Checkout form combining address and payment"""
    customer_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
            'rows': 3,
            'placeholder': 'Special instructions for your order (optional)'
        })
    )
    
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'text-accent focus:ring-accent'
        })
    )
    
    billing_same_as_shipping = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded text-accent focus:ring-accent'
        })
    )
    
    # Billing address fields (shown only if different from shipping)
    billing_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
            'rows': 3,
            'placeholder': 'Billing street address'
        })
    )
    billing_city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
            'placeholder': 'Billing city'
        })
    )
    billing_state = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
            'placeholder': 'Billing state/province'
        })
    )
    billing_country = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
            'placeholder': 'Billing country'
        })
    )
    billing_postal_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
            'placeholder': 'Billing ZIP/postal code'
        })
    )
    
    # Agreement checkboxes
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded text-accent focus:ring-accent'
        })
    )


class CouponForm(forms.Form):
    """Coupon application form"""
    code = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'px-4 py-2 border rounded-l-md focus:outline-none focus:border-accent',
            'placeholder': 'Enter coupon code'
        })
    )


class OrderStatusForm(forms.ModelForm):
    """Order status update form for staff"""
    admin_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
            'rows': 3,
            'placeholder': 'Internal notes (not visible to customer)'
        })
    )
    
    class Meta:
        model = Order
        fields = ['status', 'tracking_number', 'carrier', 'estimated_delivery', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'px-4 py-2 border rounded-md focus:outline-none focus:border-accent'
            }),
            'tracking_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
                'placeholder': 'Tracking number'
            }),
            'carrier': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
                'placeholder': 'Shipping carrier'
            }),
            'estimated_delivery': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
                'type': 'date'
            })
        }


class CartUpdateForm(forms.Form):
    """Cart item quantity update form"""
    quantity = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-20 px-2 py-1 border rounded-md focus:outline-none focus:border-accent',
            'min': '0'
        })
    )