from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product, ProductVariant
import uuid


class CartView(View):
    """Shopping cart view"""
    template_name = 'orders/cart.html'
    
    def get(self, request):
        cart = self.get_or_create_cart(request)
        context = {
            'cart': cart,
            'cart_items': cart.items.all() if cart else []
        }
        return render(request, self.template_name, context)
    
    def get_or_create_cart(self, request):
        """Get or create cart for user or session"""
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            cart, created = Cart.objects.get_or_create(
                session_key=request.session.session_key
            )
        return cart


class AddToCartView(View):
    """Add product to cart"""
    
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Get cart
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            cart, created = Cart.objects.get_or_create(
                session_key=request.session.session_key
            )
        
        # Get variant if specified
        variant_id = request.POST.get('variant_id')
        variant = None
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id)
        
        # Get quantity
        quantity = int(request.POST.get('quantity', 1))
        
        # Check if item already in cart
        cart_item = CartItem.objects.filter(
            cart=cart,
            product=product,
            variant=variant
        ).first()
        
        if cart_item:
            cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, f'Updated {product.name} quantity in cart.')
        else:
            CartItem.objects.create(
                cart=cart,
                product=product,
                variant=variant,
                quantity=quantity
            )
            messages.success(request, f'Added {product.name} to cart.')
        
        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_count': cart.total_items,
                'message': f'Added {product.name} to cart.'
            })
        
        return redirect('orders:cart')


class RemoveFromCartView(View):
    """Remove item from cart"""
    
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)
        
        # Verify ownership
        if request.user.is_authenticated:
            if cart_item.cart.user != request.user:
                messages.error(request, 'Invalid request.')
                return redirect('orders:cart')
        else:
            if cart_item.cart.session_key != request.session.session_key:
                messages.error(request, 'Invalid request.')
                return redirect('orders:cart')
        
        product_name = cart_item.product.name
        cart_item.delete()
        messages.success(request, f'Removed {product_name} from cart.')
        
        return redirect('orders:cart')


class UpdateCartItemView(View):
    """Update cart item quantity"""
    
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated.')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
        
        return redirect('orders:cart')


class CheckoutView(LoginRequiredMixin, View):
    """Checkout view"""
    template_name = 'orders/checkout.html'
    
    def get(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        
        if not cart or cart.total_items == 0:
            messages.warning(request, 'Your cart is empty.')
            return redirect('products:list')
        
        context = {
            'cart': cart,
            'cart_items': cart.items.all(),
            'user': request.user
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        
        if not cart or cart.total_items == 0:
            messages.warning(request, 'Your cart is empty.')
            return redirect('products:list')
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            customer_name=request.user.full_name,
            customer_email=request.user.email,
            customer_phone=request.user.phone_number,
            shipping_address=request.POST.get('shipping_address', request.user.address),
            shipping_city=request.POST.get('shipping_city', request.user.city),
            shipping_state=request.POST.get('shipping_state', request.user.state),
            shipping_country=request.POST.get('shipping_country', request.user.country),
            shipping_postal_code=request.POST.get('shipping_postal_code', request.user.postal_code),
            shipping_latitude=request.user.latitude,
            shipping_longitude=request.user.longitude,
            payment_method=request.POST.get('payment_method', 'cod'),
            customer_notes=request.POST.get('notes', ''),
            subtotal=cart.subtotal,
            tax=cart.tax,
            shipping=cart.shipping,
            total=cart.total
        )
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku,
                size=cart_item.variant.size if cart_item.variant else '',
                color=cart_item.variant.color if cart_item.variant else '',
                unit_price=cart_item.unit_price,
                quantity=cart_item.quantity
            )
            
            # Update stock
            if cart_item.variant:
                cart_item.variant.stock -= cart_item.quantity
                cart_item.variant.save()
            cart_item.product.total_stock -= cart_item.quantity
            cart_item.product.sales_count += cart_item.quantity
            cart_item.product.save()
        
        # Clear cart
        cart.clear()
        
        messages.success(request, 'Order placed successfully!')
        return redirect('orders:order_confirmation', order_id=order.id)


class OrderDetailView(LoginRequiredMixin, DetailView):
    """Order detail view"""
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderConfirmationView(LoginRequiredMixin, DetailView):
    """Order confirmation view"""
    model = Order
    template_name = 'orders/order_confirmation.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)