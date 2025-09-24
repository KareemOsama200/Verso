from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='list'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('new/', views.NewArrivalsView.as_view(), name='new'),
    path('sale/', views.SaleView.as_view(), name='sale'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='detail'),
    path('search/', views.SearchView.as_view(), name='search'),
]