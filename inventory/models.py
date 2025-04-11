from django.db import models

# Create your models here.
from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    location = models.CharField(max_length=100)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} - {self.location}"



class InventoryTransaction(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity_change = models.IntegerField()  # Positive for additions, negative for removals
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.item.name}: {self.quantity_change} on {self.timestamp.strftime('%Y-%m-%d')}"