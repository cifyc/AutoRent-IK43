from django.contrib import admin
from .models import Car, MaintenanceBlock

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['id', 'brand', 'model', 'city', 'daily_rate_uah', 'is_published']
    list_filter = ['city', 'category', 'is_published']
    search_fields = ['brand', 'model']

@admin.register(MaintenanceBlock)
class MaintenanceBlockAdmin(admin.ModelAdmin):
    list_display = ['id', 'car', 'starts_at', 'ends_at', 'created_by']
    # Real scheduling should go through the protected service, not direct admin writes.
