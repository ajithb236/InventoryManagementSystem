from django.contrib import admin
from . import models
# Register your models here.
from django.contrib import admin
admin.site.register(models.Item)
admin.site.register(models.Inventory)
