from datetime import datetime, timedelta

from app.services.chat import _validate_scheduled_at, CLINIC_TZ


def _next_weekday_at(hour: int, weekday: int) -> datetime:
    """Returns the next occurrence of `weekday` (Mon=0..Sun=6) at `hour`, relative to now."""
    now = datetime.now(CLINIC_TZ)
    days_ahead = (weekday - now.weekday()) % 7
    days_ahead = days_ahead if days_ahead > 0 else days_ahead + 7
    target = now + timedelta(days=days_ahead)
    return target.replace(hour=hour, minute=0, second=0, microsecond=0)


def test_rejects_past_datetime():
    past = datetime.now(CLINIC_TZ) - timedelta(days=1)
    assert _validate_scheduled_at(past) is not None


def test_rejects_weekend():
    saturday = _next_weekday_at(hour=10, weekday=5)
    assert _validate_scheduled_at(saturday) is not None


def test_rejects_before_business_hours():
    early = _next_weekday_at(hour=7, weekday=0)
    assert _validate_scheduled_at(early) is not None


def test_rejects_after_business_hours():
    late = _next_weekday_at(hour=18, weekday=0)
    assert _validate_scheduled_at(late) is not None


def test_accepts_valid_weekday_business_hours():
    valid = _next_weekday_at(hour=10, weekday=0)
    assert _validate_scheduled_at(valid) is None
