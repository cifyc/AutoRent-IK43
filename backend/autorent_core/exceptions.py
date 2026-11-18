class AutoRentError(ValueError):
    """Domain error independent from HTTP and Django."""

class InvalidPeriod(AutoRentError):
    pass

class BookingConflict(AutoRentError):
    pass

class InvalidStateTransition(AutoRentError):
    pass

class CancellationNotAllowed(AutoRentError):
    pass
