from django import forms
from django.forms import formset_factory, modelformset_factory
from .models import Product, ProductImage, ProductVideo, ProductVariant, Review, Category, Brand
from ckeditor.widgets import CKEditorWidget


class ProductForm(forms.ModelForm):
    """Product creation/edit form"""
    description = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'description', 'short_description',
            'category', 'brand', 'gender', 'base_price',
            'discount_percentage', 'discount_amount',
            'low_stock_threshold', 'features', 'care_instructions',
            'material', 'meta_title', 'meta_description', 'meta_keywords',
            'is_active', 'is_featured'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent'
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
                'rows': 3
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent'
            }),
            'brand': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent'
            }),
            'base_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
                'step': '0.01'
            }),
            'discount_percentage': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
                'step': '0.01'
            }),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
                'step': '0.01'
            }),
            'low_stock_threshold': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent'
            }),
            'care_instructions': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
                'rows': 3
            }),
            'material': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
                'rows': 2
            }),
            'meta_keywords': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded text-accent focus:ring-accent'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'rounded text-accent focus:ring-accent'
            })
        }


class ProductImageForm(forms.ModelForm):
    """Product image upload form"""
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_primary', 'display_order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent',
                'accept': 'image/*'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent'
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'rounded text-accent focus:ring-accent'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:border-accent'
            })
        }


ProductImageFormSet = modelformset_factory(
    ProductImage,
    form=ProductImageForm,
    extra=3,
    can_delete=True
)


class ProductVariantForm(forms.ModelForm):
    """Product variant form"""
    class Meta:
        model = ProductVariant
        fields = ['size', 'color', 'color_hex', 'stock', 'additional_price', 'sku_suffix']
        widgets = {
            'size': forms.Select(attrs={
                'class': 'px-3 py-1 border rounded-md focus:outline-none focus:border-accent'
            }),
            'color': forms.TextInput(attrs={
                'class': 'px-3 py-1 border rounded-md focus:outline-none focus:border-accent'
            }),
            'color_hex': forms.TextInput(attrs={
                'class': 'px-3 py-1 border rounded-md focus:outline-none focus:border-accent',
                'type': 'color'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'px-3 py-1 border rounded-md focus:outline-none focus:border-accent',
                'min': '0'
            }),
            'additional_price': forms.NumberInput(attrs={
                'class': 'px-3 py-1 border rounded-md focus:outline-none focus:border-accent',
                'step': '0.01'
            }),
            'sku_suffix': forms.TextInput(attrs={
                'class': 'px-3 py-1 border rounded-md focus:outline-none focus:border-accent'
            })
        }


ProductVariantFormSet = modelformset_factory(
    ProductVariant,
    form=ProductVariantForm,
    extra=3,
    can_delete=True
)


class AddToCartForm(forms.Form):
    """Add to cart form"""
    variant_id = forms.UUIDField(required=False, widget=forms.HiddenInput())
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-20 px-3 py-2 border rounded-md focus:outline-none focus:border-accent',
            'min': '1'
        })
    )


class ProductFilterForm(forms.Form):
    """Product filter form for category pages"""
    # Price range
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-24 px-2 py-1 border rounded-md',
            'placeholder': 'Min'
        })
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-24 px-2 py-1 border rounded-md',
            'placeholder': 'Max'
        })
    )
    
    # Size filter
    size = forms.MultipleChoiceField(
        required=False,
        choices=ProductVariant.SIZE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'text-accent focus:ring-accent'
        })
    )
    
    # Color filter  
    color = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-1 border rounded-md',
            'placeholder': 'Color'
        })
    )
    
    # Gender filter
    gender = forms.ChoiceField(
        required=False,
        choices=[('', 'All')] + Product.GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-1 border rounded-md'
        })
    )
    
    # Sort options
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('-created_at', 'Newest First'),
            ('price_low', 'Price: Low to High'),
            ('price_high', 'Price: High to Low'),
            ('name', 'Name: A-Z'),
            ('-name', 'Name: Z-A'),
            ('-sales_count', 'Best Sellers')
        ],
        widget=forms.Select(attrs={
            'class': 'px-4 py-2 border rounded-md'
        })
    )


class ReviewForm(forms.ModelForm):
    """Product review form"""
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, i) for i in range(1, 6)],
                attrs={'class': 'px-3 py-1 border rounded-md'}
            ),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md',
                'placeholder': 'Review title'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-md',
                'rows': 4,
                'placeholder': 'Write your review here...'
            })
        }