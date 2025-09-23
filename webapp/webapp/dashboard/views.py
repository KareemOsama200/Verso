from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from products.models import Product, Category, Brand
from orders.models import Order, OrderItem
import json
import csv
from django.http import HttpResponse


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to require staff access"""
    
    def test_func(self):
        return self.request.user.is_staff_member


class DashboardView(StaffRequiredMixin, View):
    """Main dashboard view"""
    template_name = 'dashboard/index.html'
    
    def get(self, request):
        # Date ranges
        today = timezone.now().date()
        last_30_days = today - timedelta(days=30)
        last_7_days = today - timedelta(days=7)
        
        # Sales statistics
        total_sales = Order.objects.filter(
            status__in=['paid', 'shipped', 'delivered']
        ).aggregate(total=Sum('total'))['total'] or 0
        
        sales_last_30_days = Order.objects.filter(
            created_at__gte=last_30_days,
            status__in=['paid', 'shipped', 'delivered']
        ).aggregate(total=Sum('total'))['total'] or 0
        
        sales_last_7_days = Order.objects.filter(
            created_at__gte=last_7_days,
            status__in=['paid', 'shipped', 'delivered']
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # Order statistics
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        processing_orders = Order.objects.filter(status='processing').count()
        
        # Recent orders
        recent_orders = Order.objects.order_by('-created_at')[:10]
        
        # Customer statistics
        total_customers = User.objects.filter(role='customer').count()
        new_customers_30_days = User.objects.filter(
            role='customer',
            created_at__gte=last_30_days
        ).count()
        
        # Product statistics
        total_products = Product.objects.filter(is_active=True).count()
        low_stock_products = Product.objects.filter(
            is_active=True,
            total_stock__lte=10
        ).count()
        
        # Best selling products
        best_sellers = Product.objects.filter(
            is_active=True
        ).order_by('-sales_count')[:5]
        
        context = {
            'total_sales': total_sales,
            'sales_last_30_days': sales_last_30_days,
            'sales_last_7_days': sales_last_7_days,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'processing_orders': processing_orders,
            'recent_orders': recent_orders,
            'total_customers': total_customers,
            'new_customers_30_days': new_customers_30_days,
            'total_products': total_products,
            'low_stock_products': low_stock_products,
            'best_sellers': best_sellers,
        }
        
        return render(request, self.template_name, context)


class ProductManagementView(StaffRequiredMixin, ListView):
    """Product management view"""
    model = Product
    template_name = 'dashboard/products.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Filter by category
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        elif status == 'low_stock':
            queryset = queryset.filter(total_stock__lte=10)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class AddProductView(StaffRequiredMixin, View):
    """Add new product view"""
    template_name = 'dashboard/add_product.html'
    
    def get(self, request):
        context = {
            'categories': Category.objects.filter(is_active=True),
            'brands': Brand.objects.filter(is_active=True)
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Here you would handle product creation
        # This is a simplified version
        messages.success(request, 'Product added successfully!')
        return redirect('dashboard:products')


class EditProductView(StaffRequiredMixin, View):
    """Edit product view"""
    template_name = 'dashboard/edit_product.html'
    
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        context = {
            'product': product,
            'categories': Category.objects.filter(is_active=True),
            'brands': Brand.objects.filter(is_active=True)
        }
        return render(request, self.template_name, context)
    
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        # Here you would handle product update
        messages.success(request, 'Product updated successfully!')
        return redirect('dashboard:products')


class OrderManagementView(StaffRequiredMixin, ListView):
    """Order management view"""
    model = Order
    template_name = 'dashboard/orders.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Order.objects.all()
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(customer_email__icontains=search)
            )
        
        return queryset.order_by('-created_at')


class CustomerManagementView(StaffRequiredMixin, ListView):
    """Customer management view"""
    model = User
    template_name = 'dashboard/customers.html'
    context_object_name = 'customers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.filter(role='customer')
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        return queryset.order_by('-created_at')


class StaffManagementView(StaffRequiredMixin, UserPassesTestMixin, ListView):
    """Staff management view"""
    model = User
    template_name = 'dashboard/staff.html'
    context_object_name = 'staff_members'
    paginate_by = 20
    
    def test_func(self):
        # Only admins and managers can manage staff
        return self.request.user.is_admin or self.request.user.is_manager
    
    def get_queryset(self):
        return User.objects.filter(
            role__in=['admin', 'manager', 'employee']
        ).order_by('-created_at')


class AnalyticsView(StaffRequiredMixin, View):
    """Analytics view"""
    template_name = 'dashboard/analytics.html'
    
    def get(self, request):
        # This would contain more complex analytics
        context = {
            'title': 'Analytics Dashboard'
        }
        return render(request, self.template_name, context)


class ExportDataView(StaffRequiredMixin, UserPassesTestMixin, View):
    """Export data view"""
    
    def test_func(self):
        # Check if user has export permission
        return self.request.user.is_admin or self.request.user.is_manager
    
    def get(self, request):
        export_type = request.GET.get('type')
        
        if export_type == 'orders':
            return self.export_orders()
        elif export_type == 'products':
            return self.export_products()
        elif export_type == 'customers':
            return self.export_customers()
        
        messages.error(request, 'Invalid export type.')
        return redirect('dashboard:index')
    
    def export_orders(self):
        """Export orders to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order Number', 'Customer', 'Email', 'Status', 'Total', 'Created At'])
        
        orders = Order.objects.all()
        for order in orders:
            writer.writerow([
                order.order_number,
                order.customer_name,
                order.customer_email,
                order.status,
                order.total,
                order.created_at
            ])
        
        return response
    
    def export_products(self):
        """Export products to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['SKU', 'Name', 'Category', 'Price', 'Stock', 'Status'])
        
        products = Product.objects.all()
        for product in products:
            writer.writerow([
                product.sku,
                product.name,
                product.category.name if product.category else '',
                product.base_price,
                product.total_stock,
                'Active' if product.is_active else 'Inactive'
            ])
        
        return response
    
    def export_customers(self):
        """Export customers to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customers.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Username', 'Email', 'Name', 'Phone', 'Created At'])
        
        customers = User.objects.filter(role='customer')
        for customer in customers:
            writer.writerow([
                customer.username,
                customer.email,
                customer.full_name,
                customer.phone_number,
                customer.created_at
            ])
        
        return response