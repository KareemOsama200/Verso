from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Brand, Product, ProductImage, ProductVideo,
    ProductVariant, Tag, Review, Wishlist
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'display_order']


class ProductVideoInline(admin.TabularInline):
    model = ProductVideo
    extra = 0
    fields = ['video', 'title', 'thumbnail', 'display_order']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['size', 'color', 'color_hex', 'stock', 'additional_price', 'sku_suffix']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'display_order', 'product_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['display_order', 'name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'brand', 'base_price', 'current_price_display', 
                    'total_stock', 'is_active', 'is_featured', 'is_new_badge']
    list_filter = ['is_active', 'is_featured', 'category', 'brand', 'gender', 'created_at']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'views_count', 'sales_count']
    inlines = [ProductImageInline, ProductVariantInline, ProductVideoInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'description', 'short_description')
        }),
        ('Categorization', {
            'fields': ('category', 'brand', 'gender')
        }),
        ('Pricing', {
            'fields': ('base_price', 'discount_percentage', 'discount_amount')
        }),
        ('Stock', {
            'fields': ('total_stock', 'low_stock_threshold')
        }),
        ('Features', {
            'fields': ('features', 'care_instructions', 'material')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('views_count', 'sales_count', 'rating', 'review_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'created_by')
        }),
    )
    
    def current_price_display(self, obj):
        if obj.is_on_sale:
            return format_html(
                '<span style="text-decoration: line-through;">${}</span> <span style="color: red;">${:.2f}</span>',
                obj.base_price, obj.current_price
            )
        return f"${obj.base_price}"
    current_price_display.short_description = 'Current Price'
    
    def is_new_badge(self, obj):
        if obj.is_new:
            return format_html('<span style="color: green;">NEW</span>')
        return ''
    is_new_badge.short_description = 'New'
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'is_primary', 'display_order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text']
    ordering = ['product', 'display_order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Preview'


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'color', 'color_preview', 'stock', 'price', 'is_available']
    list_filter = ['size', 'product__category', 'product__brand']
    search_fields = ['product__name', 'product__sku']
    
    def color_preview(self, obj):
        if obj.color_hex:
            return format_html(
                '<span style="background-color: {}; padding: 2px 10px; border: 1px solid #ccc;">{}</span>',
                obj.color_hex, obj.color
            )
        return obj.color
    color_preview.short_description = 'Color'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__username', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'product__name']
    raw_id_fields = ['user', 'product']