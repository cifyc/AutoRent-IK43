from django.db import models
from django.conf import settings
from django.db.models import F, Q


class Car(models.Model):
    brand = models.CharField(max_length=80)
    model = models.CharField(max_length=80)
    category = models.CharField(max_length=40)
    city = models.CharField(max_length=80)
    seats = models.PositiveSmallIntegerField(default=5)
    image_url = models.URLField(blank=True)
    daily_rate_uah = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_uah = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(daily_rate_uah__gte=0), name='car_nonnegative_rate'),
            models.CheckConstraint(condition=Q(deposit_uah__gte=0), name='car_nonnegative_deposit'),
            models.CheckConstraint(condition=Q(seats__gte=1), name='car_seats_positive'),
        ]

    def __str__(self):
        return f'{self.brand} {self.model} ({self.city})'


class MaintenanceBlock(models.Model):
    car = models.ForeignKey(Car, on_delete=models.PROTECT, related_name='maintenance_blocks')
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(ends_at__gt=F('starts_at')), name='maintenance_valid_interval')]
