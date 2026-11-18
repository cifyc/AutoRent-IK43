"""Pure business rules: portable and testable without third-party packages."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from .exceptions import InvalidPeriod, InvalidStateTransition, CancellationNotAllowed

DAY_US = 24 * 60 * 60 * 1_000_000
TWO_DECIMALS = Decimal('0.01')


def as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise InvalidPeriod('Потрібні дата й час із часовим поясом.')
    return dt.astimezone(timezone.utc)


@dataclass(frozen=True)
class Period:
    start: datetime
    end: datetime

    def __post_init__(self):
        if as_utc(self.end) <= as_utc(self.start):
            raise InvalidPeriod('Кінець періоду має бути пізніше початку.')

    def overlaps(self, other: 'Period') -> bool:
        """Half-open intervals [start, end): adjacent periods do not overlap."""
        return as_utc(self.start) < as_utc(other.end) and as_utc(other.start) < as_utc(self.end)


@dataclass(frozen=True)
class PriceQuote:
    days: int
    daily_rate_uah: Decimal
    total_uah: Decimal
    deposit_uah: Decimal


class PricingPolicy:
    def quote(self, period: Period, daily_rate_uah: Decimal, deposit_uah: Decimal) -> PriceQuote:
        rate, deposit = Decimal(str(daily_rate_uah)), Decimal(str(deposit_uah))
        if rate < 0 or deposit < 0:
            raise ValueError('Тариф і застава не можуть бути від’ємними.')
        elapsed: timedelta = as_utc(period.end) - as_utc(period.start)
        microseconds = (elapsed.days * 86_400 + elapsed.seconds) * 1_000_000 + elapsed.microseconds
        days = (microseconds + DAY_US - 1) // DAY_US
        return PriceQuote(
            days=days,
            daily_rate_uah=rate.quantize(TWO_DECIMALS, rounding=ROUND_HALF_UP),
            total_uah=(days * rate).quantize(TWO_DECIMALS, rounding=ROUND_HALF_UP),
            deposit_uah=deposit.quantize(TWO_DECIMALS, rounding=ROUND_HALF_UP),
        )


class BookingState(str, Enum):
    CONFIRMED = 'confirmed'
    ACTIVE = 'active'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


_ALLOWED = {
    BookingState.CONFIRMED: {BookingState.ACTIVE, BookingState.CANCELLED},
    BookingState.ACTIVE: {BookingState.COMPLETED},
    BookingState.COMPLETED: set(),
    BookingState.CANCELLED: set(),
}


def ensure_transition(current: BookingState, next_state: BookingState) -> None:
    if next_state not in _ALLOWED[current]:
        raise InvalidStateTransition(f'Перехід {current.value} -> {next_state.value} заборонено.')


def ensure_client_cancel_allowed(state: BookingState, start: datetime, now: datetime) -> None:
    if state != BookingState.CONFIRMED or as_utc(start) - as_utc(now) < timedelta(hours=24):
        raise CancellationNotAllowed('Самостійне скасування можливе не пізніше ніж за 24 год.')


def ensure_future(period: Period, now: datetime) -> None:
    if as_utc(period.start) <= as_utc(now):
        raise InvalidPeriod('Початок бронювання має бути в майбутньому.')
