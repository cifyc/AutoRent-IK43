"""Atomic booking operations. PostgreSQL row-locking is required for concurrency guarantee."""
from datetime import datetime, timezone
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from apps.catalog.models import Car, MaintenanceBlock
from .models import Booking
from autorent_core.rules import (
    BookingState, Period, PricingPolicy, ensure_client_cancel_allowed,
    ensure_future, ensure_transition,
)
from autorent_core.exceptions import BookingConflict


class BookingService:
    def __init__(self, pricing_policy=None):
        self.pricing = pricing_policy or PricingPolicy()

    @transaction.atomic
    def create(self, *, user, car_id: int, starts_at: datetime, ends_at: datetime, now=None):
        if not user.is_authenticated:
            raise PermissionDenied('Для бронювання необхідний вхід.')
        period = Period(starts_at, ends_at)
        ensure_future(period, now or datetime.now(timezone.utc))
        # Every create and maintenance operation locks the same Car row first.
        car = get_object_or_404(Car.objects.select_for_update(), pk=car_id, is_published=True)
        conflicts = Booking.objects.filter(
            car=car, status__in=[Booking.Status.CONFIRMED, Booking.Status.ACTIVE],
            starts_at__lt=ends_at, ends_at__gt=starts_at,
        )
        if conflicts.exists() or MaintenanceBlock.objects.filter(
            car=car, starts_at__lt=ends_at, ends_at__gt=starts_at,
        ).exists():
            raise BookingConflict('Автомобіль недоступний у вибраний період.')
        quote = self.pricing.quote(period, car.daily_rate_uah, car.deposit_uah)
        return Booking.objects.create(
            user=user, car=car, starts_at=starts_at, ends_at=ends_at,
            status=Booking.Status.CONFIRMED,
            daily_rate_snapshot_uah=quote.daily_rate_uah,
            billable_days=quote.days, total_uah=quote.total_uah,
            deposit_snapshot_uah=quote.deposit_uah,
        )

    @transaction.atomic
    def cancel_for_client(self, *, user, booking_id: int, now=None):
        obj = get_object_or_404(Booking.objects.select_for_update(), pk=booking_id, user=user)
        ensure_client_cancel_allowed(BookingState(obj.status), obj.starts_at, now or datetime.now(timezone.utc))
        obj.status = Booking.Status.CANCELLED
        obj.save(update_fields=['status'])
        return obj

    @transaction.atomic
    def move_by_manager(self, *, manager, booking_id: int, next_state: BookingState, reason: str = ''):
        if not manager.is_staff:
            raise PermissionDenied('Доступ лише для менеджера.')
        booking = get_object_or_404(Booking.objects.select_for_update(), pk=booking_id)
        ensure_transition(BookingState(booking.status), next_state)
        booking.status = next_state.value
        if next_state == BookingState.CANCELLED:
            if not reason.strip():
                raise ValueError('Менеджер повинен указати причину скасування.')
            booking.cancel_reason = reason.strip()
        booking.save(update_fields=['status', 'cancel_reason'])
        return booking

    @transaction.atomic
    def create_maintenance(self, *, manager, car_id: int, starts_at, ends_at, reason: str = ''):
        if not manager.is_staff:
            raise PermissionDenied('Доступ лише для менеджера.')
        Period(starts_at, ends_at)
        car = get_object_or_404(Car.objects.select_for_update(), pk=car_id)
        if Booking.objects.filter(
            car=car, status__in=[Booking.Status.CONFIRMED, Booking.Status.ACTIVE],
            starts_at__lt=ends_at, ends_at__gt=starts_at,
        ).exists() or MaintenanceBlock.objects.filter(
            car=car, starts_at__lt=ends_at, ends_at__gt=starts_at,
        ).exists():
            raise BookingConflict('ТО перетинається з бронюванням або іншим ТО.')
        return MaintenanceBlock.objects.create(
            car=car, starts_at=starts_at, ends_at=ends_at, reason=reason, created_by=manager,
        )
