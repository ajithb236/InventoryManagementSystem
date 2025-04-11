from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('manage/', views.manage_inventory, name='manage_inventory'),
    path('edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete/<int:item_id>/', views.delete_item, name='delete_item'),
    path('locations/<int:item_id>/', views.item_locations, name='item_locations'),
    path('analytics/', views.inventory_analytics, name='inventory_analytics'),  # Add this line
]