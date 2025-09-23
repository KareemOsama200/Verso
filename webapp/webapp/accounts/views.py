from django.shortcuts import render, redirect
from django.views.generic import View, ListView, DetailView
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import User, CustomerProfile
from orders.models import Order
from products.models import Wishlist


class LoginView(View):
    """User login view"""
    template_name = 'accounts/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, self.template_name)
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            # Redirect to next URL or appropriate dashboard
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            elif user.is_staff_member:
                return redirect('dashboard:index')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, self.template_name)


class RegisterView(View):
    """User registration view"""
    template_name = 'accounts/register.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, self.template_name)
    
    def post(self, request):
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        
        # Validation
        errors = []
        
        if not username or not email or not password:
            errors.append('Please fill in all required fields.')
        
        if password != password2:
            errors.append('Passwords do not match.')
        
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        
        if User.objects.filter(username=username).exists():
            errors.append('Username already exists.')
        
        if User.objects.filter(email=email).exists():
            errors.append('Email already registered.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, self.template_name)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            role='customer'
        )
        
        # Create customer profile
        CustomerProfile.objects.create(user=user)
        
        # Log the user in
        login(request, user)
        messages.success(request, 'Registration successful! Welcome to Verso Store.')
        
        return redirect('home')


class ProfileView(LoginRequiredMixin, View):
    """User profile view"""
    template_name = 'accounts/profile.html'
    login_url = reverse_lazy('accounts:login')
    
    def get(self, request):
        context = {
            'user': request.user,
            'recent_orders': Order.objects.filter(user=request.user).order_by('-created_at')[:5]
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        user = request.user
        
        # Update user information
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.address = request.POST.get('address', user.address)
        user.city = request.POST.get('city', user.city)
        user.state = request.POST.get('state', user.state)
        user.country = request.POST.get('country', user.country)
        user.postal_code = request.POST.get('postal_code', user.postal_code)
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        
        return redirect('accounts:profile')


class OrderListView(LoginRequiredMixin, ListView):
    """User orders list view"""
    template_name = 'accounts/orders.html'
    context_object_name = 'orders'
    paginate_by = 10
    login_url = reverse_lazy('accounts:login')
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class WishlistView(LoginRequiredMixin, ListView):
    """User wishlist view"""
    template_name = 'accounts/wishlist.html'
    context_object_name = 'wishlist_items'
    login_url = reverse_lazy('accounts:login')
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')