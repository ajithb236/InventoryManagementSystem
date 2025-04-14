from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Item, Inventory
from django import forms
from django.db.models import Sum, Count
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'quantity']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['item', 'location']

@login_required
def dashboard_view(request):
    """Dashboard view for authenticated users."""
    items_count = Item.objects.count()
    low_stock_items = Item.objects.filter(quantity__lt=10)
    locations = Inventory.objects.values('location').distinct().count()
    
    context = {
        'items_count': items_count,
        'low_stock_items': low_stock_items,
        'locations_count': locations
    }
    return render(request, 'inventory/dashboard.html', context)

@login_required
def manage_inventory(request):
    """View for managing inventory items"""
    items = Item.objects.all().order_by('name')
    
    # Get search parameter
    search_query = request.GET.get('search', '')
    if search_query:
        items = items.filter(name__icontains=search_query)
    filter_param = request.GET.get('filter', '')
    if filter_param == 'low_stock':
        items = items.filter(quantity__lt=10)
    
    # Handle item creation
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            quantity = request.POST.get('quantity', 0)
            
            if not name:
                messages.error(request, "Item name is required")
            else:
                # Create the item
                Item.objects.create(
                    name=name,
                    description=description,
                    quantity=int(quantity)
                )

                # Use redirect object instead of name
                return redirect('manage_inventory')
        except Exception as e:
            messages.error(request, f"Error adding item: {str(e)}")
    
    context = {
        'items': items,
        'search_query': search_query
    }
    return render(request, 'inventory/manage_inventory.html', context)
@login_required
def edit_item(request, item_id):
    """View for editing an inventory item"""
    item = get_object_or_404(Item, id=item_id)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"Item '{item.name}' updated successfully!")
            return redirect('manage_inventory')
    else:
        form = ItemForm(instance=item)
    
    return render(request, 'inventory/edit_item.html', {'form': form, 'item': item})

@login_required
def delete_item(request, item_id):
    """View for deleting an inventory item"""
    item = get_object_or_404(Item, id=item_id)
    
    if request.method == 'POST':
        item_name = item.name
        item.delete()
        messages.success(request, f"Item '{item_name}' deleted successfully!")
        return redirect('manage_inventory')
    
    return render(request, 'inventory/delete_item.html', {'item': item})

@login_required
def item_locations(request, item_id):
    """View item's location history"""
    item = get_object_or_404(Item, id=item_id)
    locations = Inventory.objects.filter(item=item).order_by('-date_added')
    
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            new_location = form.save(commit=False)
            new_location.item = item
            new_location.save()
            messages.success(request, f"Location added for '{item.name}'!")
            return redirect('item_locations', item_id=item.id)
    else:
        form = InventoryForm(initial={'item': item})
        form.fields['item'].widget = forms.HiddenInput()
        
    context = {
        'item': item,
        'locations': locations,
        'form': form
    }
    return render(request, 'inventory/item_locations.html', context)





@login_required
def inventory_analytics(request):
    """View for inventory analytics dashboard"""
    # Get overall statistics
    total_items = Item.objects.count()
    total_quantity = Item.objects.aggregate(total=Sum('quantity'))['total'] or 0  # Changed from models.Sum to Sum
    low_stock_count = Item.objects.filter(quantity__lt=10).count()
    
    # Location distribution
    location_data = Inventory.objects.values('location').annotate(
        count=Count('item')  # Changed from models.Count to Count
    ).order_by('-count')
    
    # Most and least stocked items
    most_stocked = Item.objects.order_by('-quantity')[:5]
    least_stocked = Item.objects.order_by('quantity')[:5]
    
    # Get monthly aggregated data (for charts)
    monthly_data = {
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'values': [150, 170, 180, 160, 200, 220]
    }
    
    context = {
        'total_items': total_items,
        'total_quantity': total_quantity,
        'low_stock_count': low_stock_count,
        'low_stock_percentage': (low_stock_count / total_items * 100) if total_items > 0 else 0,
        'location_data': location_data,
        'most_stocked': most_stocked,
        'least_stocked': least_stocked,
        'monthly_data': monthly_data,
    }
    
    return render(request, 'inventory/analytics.html', context)


@login_required
def view_locations(request):
    """View all inventory locations"""
    # Get unique locations with item counts
    locations = Inventory.objects.values('location').annotate(
        item_count=Count('item', distinct=True)
    ).order_by('location')
    
    # Get search parameter
    search_query = request.GET.get('search', '')
    if search_query:
        locations = locations.filter(location__icontains=search_query)
    
    # Count total unique locations
    total_locations = locations.count()
    
    context = {
        'locations': locations,
        'total_locations': total_locations,
        'search_query': search_query
    }
    return render(request, 'inventory/view_locations.html', context)

@login_required
def location_items(request, location):
    """View all items at a specific location"""
    # Get all inventory records for this location
    inventory_items = Inventory.objects.filter(location=location).select_related('item')
    
    # Get unique items at this location (most recent entries)
    items = []
    item_ids = set()
    
    for inv in inventory_items:
        if inv.item.id not in item_ids:
            items.append(inv.item)
            item_ids.add(inv.item.id)
    
    context = {
        'location': location,
        'items': items,
        'items_count': len(items)
    }
    return render(request, 'inventory/location_items.html', context)