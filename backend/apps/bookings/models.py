from uuid import uuid4
from django.conf import settings
from django.db import models
from django.db.models import F, Q


def new_booking_number():
    return uuid4().hex[:16].upper()


class Booking(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = 'confirmed', 'Підтверджено'
        ACTIVE = 'active', 'Активна'
        COMPLETED = 'completed', 'Завершена'
        CANCELLED = 'cancelled', 'Скасована'

    number = models.CharField(max_length=16, unique=True, default=new_booking_number, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='rentals')
    car = models.ForeignKey('catalog.Car', on_delete=models.PROTECT, related_name='bookings')
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.CONFIRMED)
    daily_rate_snapshot_uah = models.DecimalField(max_digits=10, decimal_places=2)
    billable_days = models.PositiveIntegerField()
    total_uah = models.DecimalField(max_digits=12, decimal_places=2)
    deposit_snapshot_uah = models.DecimalField(max_digits=10, decimal_places=2)
    cancel_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(ends_at__gt=F('starts_at')), name='booking_valid_interval')]
        ordering = ['-created_at']

    def __str__(self):
        return self.number
