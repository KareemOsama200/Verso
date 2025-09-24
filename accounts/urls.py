from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('orders/', views.OrderListView.as_view(), name='orders'),
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
]