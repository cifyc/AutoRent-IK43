from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['number', 'user', 'car', 'status', 'starts_at', 'ends_at', 'total_uah']
    list_filter = ['status']
    search_fields = ['number', 'user__username']
    readonly_fields = [
        'number', 'user', 'car', 'starts_at', 'ends_at',
        'daily_rate_snapshot_uah', 'billable_days', 'total_uah',
        'deposit_snapshot_uah', 'created_at', 'status',
    ]
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
