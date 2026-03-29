from datetime import datetime

import pytest

from src.models import EventDateTime


@pytest.mark.parametrize(
    ("date_time", "time_zone", "expected_snippet"),
    [
        (
            datetime(2024, 6, 15, 14, 30),
            "Europe/London",
            "2024-06-15 14:30:00",
        ),
        (datetime(2020, 1, 1), "UTC", "2020-01-01 00:00:00"),
    ],
)
def test_str_includes_local_datetime_and_zone(date_time: datetime, time_zone: str, expected_snippet: str) -> None:
    edt = EventDateTime(date_time=date_time, time_zone=time_zone)
    text = str(edt)
    assert expected_snippet in text
    assert time_zone in text


def test_from_dict_parses_iso_datetime() -> None:
    edt = EventDateTime.from_dict({"dateTime": "2024-06-15T14:30:00", "timeZone": "Europe/London"})
    assert edt.time_zone == "Europe/London"
    assert edt.date_time.year == 2024
    assert edt.date_time.month == 6
    assert edt.date_time.day == 15


def test_from_dict_default_empty_timezone() -> None:
    edt = EventDateTime.from_dict({"dateTime": "2024-01-01T00:00:00"})
    assert edt.time_zone == ""


def test_serialise_for_google() -> None:
    dt = datetime(2024, 3, 1, 12)
    edt = EventDateTime(date_time=dt, time_zone="UTC")
    assert edt.serialise_for_google() == {"dateTime": "2024-03-01T12:00:00", "timeZone": "UTC"}
