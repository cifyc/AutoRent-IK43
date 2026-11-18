"""Executable without Django: python -m unittest discover -s tests -v"""
import sys
import unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from autorent_core.rules import (
    Period, PricingPolicy, BookingState, ensure_transition, ensure_client_cancel_allowed,
    ensure_future,
)
from autorent_core.exceptions import InvalidPeriod, InvalidStateTransition, CancellationNotAllowed

UTC = timezone.utc
T0 = datetime(2027, 1, 5, 12, 0, tzinfo=UTC)

class RulesTests(unittest.TestCase):
    def test_49_hours_cost_three_days(self):
        p = Period(T0, T0 + timedelta(hours=49))
        quote = PricingPolicy().quote(p, Decimal('1200.00'), Decimal('5000.00'))
        self.assertEqual(quote.days, 3)
        self.assertEqual(quote.total_uah, Decimal('3600.00'))
        self.assertEqual(quote.deposit_uah, Decimal('5000.00'))

    def test_exact_48_hours_two_days(self):
        q = PricingPolicy().quote(Period(T0, T0 + timedelta(hours=48)), 1200, 0)
        self.assertEqual(q.days, 2)

    def test_one_microsecond_extra_starts_next_day(self):
        q = PricingPolicy().quote(Period(T0, T0 + timedelta(hours=24, microseconds=1)), 1, 0)
        self.assertEqual(q.days, 2)

    def test_adjacent_periods_do_not_overlap(self):
        a = Period(T0, T0 + timedelta(hours=1))
        b = Period(T0 + timedelta(hours=1), T0 + timedelta(hours=2))
        self.assertFalse(a.overlaps(b))

    def test_intersecting_periods_overlap(self):
        a = Period(T0, T0 + timedelta(hours=2))
        b = Period(T0 + timedelta(hours=1), T0 + timedelta(hours=3))
        self.assertTrue(a.overlaps(b))

    def test_invalid_interval_rejected(self):
        with self.assertRaises(InvalidPeriod):
            Period(T0, T0)

    def test_naive_time_rejected(self):
        with self.assertRaises(InvalidPeriod):
            Period(datetime(2027, 1, 1), datetime(2027, 1, 2))

    def test_future_required(self):
        with self.assertRaises(InvalidPeriod):
            ensure_future(Period(T0, T0 + timedelta(hours=1)), T0)

    def test_state_transitions(self):
        ensure_transition(BookingState.CONFIRMED, BookingState.ACTIVE)
        ensure_transition(BookingState.ACTIVE, BookingState.COMPLETED)
        with self.assertRaises(InvalidStateTransition):
            ensure_transition(BookingState.COMPLETED, BookingState.CONFIRMED)

    def test_cancel_25_hours_yes(self):
        ensure_client_cancel_allowed(BookingState.CONFIRMED, T0, T0 - timedelta(hours=25))

    def test_cancel_23_hours_no(self):
        with self.assertRaises(CancellationNotAllowed):
            ensure_client_cancel_allowed(BookingState.CONFIRMED, T0, T0 - timedelta(hours=23))

    def test_cancel_at_exact_24_hours_yes(self):
        ensure_client_cancel_allowed(BookingState.CONFIRMED, T0, T0 - timedelta(hours=24))

    def test_timezone_dst_elapsed_real_24h(self):
        kyiv = ZoneInfo('Europe/Kyiv')
        # Spring DST switch: local 12:00 -> 12:00 next day is 23 actual hours.
        a = datetime(2027, 3, 27, 12, tzinfo=kyiv)
        b = datetime(2027, 3, 28, 12, tzinfo=kyiv)
        self.assertEqual(PricingPolicy().quote(Period(a, b), 100, 0).days, 1)

    def test_dst_autumn_extra_hour_is_two_paid_days(self):
        kyiv = ZoneInfo('Europe/Kyiv')
        # Verified historic autumn transition, 25 actual hours in this interval.
        start = datetime(2024, 10, 26, 12, tzinfo=kyiv)
        finish = datetime(2024, 10, 27, 12, tzinfo=kyiv)
        quote = PricingPolicy().quote(Period(start, finish), '100.00', '300.00')
        self.assertEqual(quote.days, 2)
        self.assertEqual(quote.total_uah, Decimal('200.00'))

    def test_deposit_is_not_added_to_rental_total(self):
        quote = PricingPolicy().quote(Period(T0, T0 + timedelta(hours=2)), '900.00', '5000.00')
        self.assertEqual(quote.total_uah, Decimal('900.00'))
        self.assertEqual(quote.deposit_uah, Decimal('5000.00'))

    def test_cancel_active_booking_is_forbidden(self):
        with self.assertRaises(CancellationNotAllowed):
            ensure_client_cancel_allowed(BookingState.ACTIVE, T0, T0 - timedelta(days=3))

    def test_cancelled_booking_has_no_outgoing_transition(self):
        with self.assertRaises(InvalidStateTransition):
            ensure_transition(BookingState.CANCELLED, BookingState.ACTIVE)

    def test_overlap_handles_different_timezones(self):
        kyiv = ZoneInfo('Europe/Kyiv')
        utc_period = Period(datetime(2024, 1, 10, 10, tzinfo=UTC), datetime(2024, 1, 10, 11, tzinfo=UTC))
        local_period = Period(datetime(2024, 1, 10, 12, 30, tzinfo=kyiv), datetime(2024, 1, 10, 13, 30, tzinfo=kyiv))
        self.assertTrue(utc_period.overlaps(local_period))

    def test_rate_stays_decimal(self):
        q = PricingPolicy().quote(Period(T0, T0 + timedelta(hours=1)), '1234.56', '10.00')
        self.assertEqual(q.total_uah, Decimal('1234.56'))

    def test_negative_rate_rejected(self):
        with self.assertRaises(ValueError):
            PricingPolicy().quote(Period(T0, T0 + timedelta(hours=1)), '-1', 0)

if __name__ == '__main__':
    unittest.main()
