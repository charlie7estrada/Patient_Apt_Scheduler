from datetime import datetime, timedelta
from app.services.chat import _validate_scheduled_at, CLINIC_TZ


def _next_weekday_at(hour: int, weekday: int, minute: int = 0) -> datetime:
    """Returns the next occurrence of `weekday` (Mon=0..Sun=6) at `hour`, relative to now."""
    now = datetime.now(CLINIC_TZ)
    days_ahead = (weekday - now.weekday()) % 7
    days_ahead = days_ahead if days_ahead > 0 else days_ahead + 7
    target = now + timedelta(days=days_ahead)
    return target.replace(hour=hour, minute=minute, second=0, microsecond=0)


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


def test_rejects_off_grid_minute():
    off_grid = _next_weekday_at(hour=9, weekday=0, minute=1)
    assert _validate_scheduled_at(off_grid) is not None


def test_rejects_minute_inside_a_slot():
    off_grid = _next_weekday_at(hour=9, weekday=0, minute=20)
    assert _validate_scheduled_at(off_grid) is not None


def test_accepts_every_quarter_hour():
    for minute in (0, 15, 30, 45):
        slot = _next_weekday_at(hour=10, weekday=0, minute=minute)
        assert _validate_scheduled_at(slot) is None, minute


def test_accepts_first_slot_of_day():
    assert _validate_scheduled_at(_next_weekday_at(hour=9, weekday=0)) is None


def test_accepts_last_slot_of_day():
    assert _validate_scheduled_at(_next_weekday_at(hour=16, weekday=0, minute=30)) is None


def test_rejects_start_that_runs_past_closing():
    too_late = _next_weekday_at(hour=16, weekday=0, minute=45)
    assert _validate_scheduled_at(too_late) is not None
