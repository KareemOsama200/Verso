from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Category, ProductVariant, Wishlist
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import TemplateView


class HomeView(View):
    """Homepage view"""
    def get(self, request):
        # Featured products
        featured_products = Product.objects.filter(
            is_active=True, 
            is_featured=True
        )[:8]
        
        # New arrivals
        new_arrivals = Product.objects.filter(
            is_active=True
        ).order_by('-created_at')[:8]
        
        # Sale items
        sale_items = Product.objects.filter(
            is_active=True
        ).exclude(
            discount_percentage=0,
            discount_amount=0
        )[:8]
        
        # Categories
        categories = Category.objects.filter(
            is_active=True, 
            parent__isnull=True
        )
        
        context = {
            'featured_products': featured_products,
            'new_arrivals': new_arrivals,
            'sale_items': sale_items,
            'categories': categories,
        }
        
        return render(request, 'home.html', context)


class ProductListView(ListView):
    """Product listing page"""
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        
        # Filter by gender
        gender = self.request.GET.get('gender')
        if gender:
            queryset = queryset.filter(gender=gender)
        
        # Filter by price range
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)
        
        # Sorting
        sort = self.request.GET.get('sort', '-created_at')
        if sort == 'price_low':
            queryset = queryset.order_by('base_price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-base_price')
        elif sort == 'name':
            queryset = queryset.order_by('name')
        else:
            queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['current_category'] = self.request.GET.get('category')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        return context


class CategoryView(ProductListView):
    """Category specific product listing"""
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        queryset = Product.objects.filter(
            is_active=True,
            category=self.category
        )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class NewArrivalsView(ProductListView):
    """New arrivals page"""
    template_name = 'products/new_arrivals.html'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).order_by('-created_at')


class SaleView(ProductListView):
    """Sale items page"""
    template_name = 'products/sale.html'
    
    def get_queryset(self):
        return Product.objects.filter(
            is_active=True
        ).exclude(
            discount_percentage=0,
            discount_amount=0
        )


class ProductDetailView(DetailView):
    """Product detail page"""
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_object(self):
        obj = super().get_object()
        # Increment view count
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Get available sizes and colors
        context['available_sizes'] = product.get_available_sizes()
        context['available_colors'] = product.get_available_colors()
        
        # Get variants
        context['variants'] = product.variants.filter(stock__gt=0)
        
        # Related products
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:4]
        
        # Check if in wishlist
        if self.request.user.is_authenticated:
            context['in_wishlist'] = Wishlist.objects.filter(
                user=self.request.user,
                product=product
            ).exists()
        
        return context


class AboutView(TemplateView):
    """About page"""
    template_name = 'about.html'


class ContactView(TemplateView):
    """Contact page"""
    template_name = 'contact.html'


class SearchView(ListView):
    """Product search view"""
    model = Product
    template_name = 'products/search.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(sku__icontains=query) |
                Q(category__name__icontains=query) |
                Q(brand__name__icontains=query),
                is_active=True
            ).distinct()
        return Product.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context