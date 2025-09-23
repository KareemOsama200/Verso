from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='index'),
    path('products/', views.ProductManagementView.as_view(), name='products'),
    path('products/add/', views.AddProductView.as_view(), name='add_product'),
    path('products/edit/<uuid:product_id>/', views.EditProductView.as_view(), name='edit_product'),
    path('orders/', views.OrderManagementView.as_view(), name='orders'),
    path('customers/', views.CustomerManagementView.as_view(), name='customers'),
    path('staff/', views.StaffManagementView.as_view(), name='staff'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('export/', views.ExportDataView.as_view(), name='export'),
]