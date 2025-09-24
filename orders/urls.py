from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('add/<uuid:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('remove/<uuid:item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('update/<uuid:item_id>/', views.UpdateCartItemView.as_view(), name='update_cart_item'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order/<uuid:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('order/<uuid:order_id>/confirmation/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
]