"""Database-backed smoke tests; require Django and a migrated test database."""
from datetime import timedelta
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from apps.catalog.models import Car, MaintenanceBlock
from .models import Booking
from .services import BookingService
from autorent_core.exceptions import BookingConflict

class BookingServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='client', password='test-secret')
        self.manager = User.objects.create_user(username='manager', password='test-secret', is_staff=True)
        self.car = Car.objects.create(brand='Toyota', model='Corolla', category='Sedan', city='Київ', daily_rate_uah=Decimal('1200.00'), deposit_uah=Decimal('5000.00'))
        self.start = timezone.now() + timedelta(days=5)
        self.end = self.start + timedelta(hours=49)

    def test_create_and_snapshot(self):
        b = BookingService().create(user=self.user, car_id=self.car.id, starts_at=self.start, ends_at=self.end)
        self.assertEqual(b.billable_days, 3)
        self.assertEqual(b.total_uah, Decimal('3600.00'))
        self.car.daily_rate_uah = Decimal('1500.00')
        self.car.save(update_fields=['daily_rate_uah'])
        b.refresh_from_db()
        self.assertEqual(b.total_uah, Decimal('3600.00'))

    def test_double_booking_rejected_sequentially(self):
        BookingService().create(user=self.user, car_id=self.car.id, starts_at=self.start, ends_at=self.end)
        with self.assertRaises(BookingConflict):
            BookingService().create(user=self.user, car_id=self.car.id, starts_at=self.start + timedelta(hours=1), ends_at=self.end)
        self.assertEqual(Booking.objects.count(), 1)

    def test_adjacent_booking_allowed(self):
        BookingService().create(user=self.user, car_id=self.car.id, starts_at=self.start, ends_at=self.end)
        BookingService().create(user=self.user, car_id=self.car.id, starts_at=self.end, ends_at=self.end + timedelta(days=1))
        self.assertEqual(Booking.objects.count(), 2)

    def test_maintenance_block_prevents_booking(self):
        BookingService().create_maintenance(manager=self.manager, car_id=self.car.id, starts_at=self.start, ends_at=self.end)
        with self.assertRaises(BookingConflict):
            BookingService().create(user=self.user, car_id=self.car.id, starts_at=self.start, ends_at=self.end)
