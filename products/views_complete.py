"""Complete product views with all features"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Avg, F
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta

from .models import Product, Category, ProductVariant, Wishlist, Review, ProductImage, ProductVideo
from .forms import AddToCartForm, ProductFilterForm, ReviewForm, ProductForm, ProductVariantFormSet, ProductImageFormSet
from orders.models import Cart, CartItem
from dashboard.models import SiteSettings


class HomeView(View):
    """Enhanced homepage with all sections"""
    def get(self, request):
        settings = SiteSettings.get_settings()
        
        # Hero products (featured and new)
        hero_products = Product.objects.filter(
            is_active=True, 
            is_featured=True
        ).order_by('-created_at')[:3]
        
        # Featured collections (categories with products)
        featured_collections = Category.objects.filter(
            is_active=True,
            parent__isnull=True
        ).annotate(
            product_count=Count('products')
        ).filter(product_count__gt=0)[:6]
        
        # New arrivals carousel (last N days)
        new_days = settings.new_product_days
        cutoff_date = timezone.now() - timedelta(days=new_days)
        new_arrivals = Product.objects.filter(
            is_active=True,
            created_at__gte=cutoff_date
        ).order_by('-created_at')[:12]
        
        # Sale items
        sale_items = Product.objects.filter(
            is_active=True
        ).exclude(
            discount_percentage=0,
            discount_amount=0
        ).order_by('-discount_percentage')[:8]
        
        # Best sellers
        best_sellers = Product.objects.filter(
            is_active=True
        ).order_by('-sales_count')[:8]
        
        # Promo banners (could be from a Banner model, using static for now)
        promo_banners = [
            {
                'title': 'Summer Collection',
                'subtitle': 'Up to 50% Off',
                'image': 'https://via.placeholder.com/1200x400',
                'link': '/products/?collection=summer'
            },
            {
                'title': 'New Arrivals',
                'subtitle': 'Shop the Latest Trends',
                'image': 'https://via.placeholder.com/1200x400',
                'link': '/products/new/'
            }
        ]
        
        context = {
            'hero_products': hero_products,
            'featured_collections': featured_collections,
            'new_arrivals': new_arrivals,
            'sale_items': sale_items,
            'best_sellers': best_sellers,
            'promo_banners': promo_banners,
            'settings': settings,
        }
        
        return render(request, 'home_complete.html', context)


class ProductListView(ListView):
    """Enhanced product listing with filters and sorting"""
    model = Product
    template_name = 'products/list_complete.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category', 'brand')
        
        # Get filter form
        self.filter_form = ProductFilterForm(self.request.GET)
        
        # Category filter
        category_slug = self.kwargs.get('slug') or self.request.GET.get('category')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(
                Q(category=category) | Q(category__parent=category)
            )
            self.category = category
        
        # Apply filters from form
        if self.filter_form.is_valid():
            # Price range
            min_price = self.filter_form.cleaned_data.get('min_price')
            max_price = self.filter_form.cleaned_data.get('max_price')
            if min_price:
                queryset = queryset.filter(base_price__gte=min_price)
            if max_price:
                queryset = queryset.filter(base_price__lte=max_price)
            
            # Size filter
            sizes = self.filter_form.cleaned_data.get('size')
            if sizes:
                queryset = queryset.filter(variants__size__in=sizes).distinct()
            
            # Color filter
            color = self.filter_form.cleaned_data.get('color')
            if color:
                queryset = queryset.filter(variants__color__icontains=color).distinct()
            
            # Gender filter
            gender = self.filter_form.cleaned_data.get('gender')
            if gender:
                queryset = queryset.filter(gender=gender)
            
            # Sorting
            sort = self.filter_form.cleaned_data.get('sort', '-created_at')
            if sort == 'price_low':
                queryset = queryset.order_by('base_price')
            elif sort == 'price_high':
                queryset = queryset.order_by('-base_price')
            else:
                queryset = queryset.order_by(sort)
        
        # Search query
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(sku__icontains=query)
            )
        
        # Tag filter
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.filter_form
        context['categories'] = Category.objects.filter(is_active=True, parent__isnull=True)
        
        # Get available sizes and colors for current queryset
        products = self.get_queryset()
        context['available_sizes'] = ProductVariant.objects.filter(
            product__in=products
        ).values_list('size', flat=True).distinct()
        
        context['available_colors'] = ProductVariant.objects.filter(
            product__in=products
        ).values_list('color', flat=True).distinct()[:10]  # Limit to 10 colors
        
        # Breadcrumb
        if hasattr(self, 'category'):
            context['category'] = self.category
            context['breadcrumb'] = self._get_category_breadcrumb(self.category)
        
        # SEO
        context['page_title'] = getattr(self, 'category', Category(name='Shop')).name
        context['page_description'] = f"Shop {context['page_title']} at Verso Store"
        
        return context
    
    def _get_category_breadcrumb(self, category):
        """Build category breadcrumb"""
        breadcrumb = []
        current = category
        while current:
            breadcrumb.insert(0, current)
            current = current.parent
        return breadcrumb


class ProductDetailView(DetailView):
    """Enhanced product detail page"""
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_object(self):
        obj = super().get_object()
        # Increment view count
        obj.views_count = F('views_count') + 1
        obj.save(update_fields=['views_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Get variants with stock
        context['variants'] = product.variants.filter(stock__gt=0)
        context['available_sizes'] = context['variants'].values_list('size', flat=True).distinct()
        context['available_colors'] = context['variants'].values_list('color', 'color_hex').distinct()
        
        # Add to cart form
        context['add_to_cart_form'] = AddToCartForm()
        
        # Related products
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:4]
        
        # Reviews with pagination
        reviews = product.reviews.select_related('user').order_by('-created_at')
        context['reviews'] = reviews[:5]  # Show first 5
        context['review_form'] = ReviewForm() if self.request.user.is_authenticated else None
        
        # Check if in wishlist
        if self.request.user.is_authenticated:
            context['in_wishlist'] = Wishlist.objects.filter(
                user=self.request.user,
                product=product
            ).exists()
        
        # Breadcrumb
        context['breadcrumb'] = self._get_product_breadcrumb(product)
        
        # Settings
        context['settings'] = SiteSettings.get_settings()
        
        return context
    
    def _get_product_breadcrumb(self, product):
        """Build product breadcrumb"""
        breadcrumb = [
            {'name': 'Home', 'url': '/'},
            {'name': 'Shop', 'url': '/products/'}
        ]
        
        if product.category:
            current = product.category
            category_crumbs = []
            while current:
                category_crumbs.insert(0, {
                    'name': current.name,
                    'url': f'/products/category/{current.slug}/'
                })
                current = current.parent
            breadcrumb.extend(category_crumbs)
        
        breadcrumb.append({'name': product.name, 'url': None})
        return breadcrumb


class QuickViewModal(View):
    """AJAX endpoint for quick view modal"""
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Get basic product info
        data = {
            'id': str(product.id),
            'name': product.name,
            'price': float(product.current_price),
            'original_price': float(product.base_price),
            'description': product.short_description,
            'image': product.main_image.image.url if product.main_image else '',
            'is_on_sale': product.is_on_sale,
            'discount_percentage': float(product.discount_percentage),
            'in_stock': product.total_stock > 0,
            'sizes': list(product.variants.filter(stock__gt=0).values_list('size', flat=True).distinct()),
            'url': f'/products/{product.slug}/'
        }
        
        return JsonResponse(data)


class AddToWishlistView(LoginRequiredMixin, View):
    """Add/remove product from wishlist"""
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if not created:
            wishlist_item.delete()
            message = 'Removed from wishlist'
            added = False
        else:
            message = 'Added to wishlist'
            added = True
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': message,
                'added': added,
                'wishlist_count': request.user.wishlists.count()
            })
        
        messages.success(request, message)
        return redirect(request.META.get('HTTP_REFERER', 'products:list'))


class WriteReviewView(LoginRequiredMixin, View):
    """Submit product review"""
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        form = ReviewForm(request.POST)
        
        if form.is_valid():
            # Check if user already reviewed this product
            existing_review = Review.objects.filter(
                product=product,
                user=request.user
            ).first()
            
            if existing_review:
                # Update existing review
                existing_review.rating = form.cleaned_data['rating']
                existing_review.title = form.cleaned_data['title']
                existing_review.comment = form.cleaned_data['comment']
                existing_review.save()
                messages.success(request, 'Your review has been updated.')
            else:
                # Create new review
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                
                # Check if verified purchase
                review.is_verified_purchase = request.user.orders.filter(
                    items__product=product,
                    status='delivered'
                ).exists()
                
                review.save()
                
                # Update product rating
                product.update_rating()
                
                messages.success(request, 'Thank you for your review!')
        else:
            messages.error(request, 'Please correct the errors in your review.')
        
        return redirect('products:detail', slug=product.slug)