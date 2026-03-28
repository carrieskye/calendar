from src.models.calendar import Calendar, Owner
from src.models.event import Event
from src.models.event_datetime import EventDateTime


def _sample_calendar() -> Calendar:
    return Calendar(name="work", user="cal_user", partner="cal_partner", shared="")


def test_event_serialise_for_google_structure() -> None:
    start = EventDateTime.from_dict({"dateTime": "2024-06-01T10:00:00", "timeZone": "Europe/London"})
    end = EventDateTime.from_dict({"dateTime": "2024-06-01T11:00:00", "timeZone": "Europe/London"})
    event = Event(
        summary="Meeting",
        location="Cardiff",
        description="Notes",
        start=start,
        end=end,
        calendar=_sample_calendar(),
        owner=Owner.user,
    )
    payload = event.serialise_for_google()
    assert payload["summary"] == "Meeting"
    assert payload["location"] == "Cardiff"
    assert payload["description"] == "Notes"
    assert payload["visibility"] == "default"
    assert payload["start"] == start.serialise_for_google()
    assert payload["end"] == end.serialise_for_google()


def test_event_from_dict() -> None:
    cal = _sample_calendar()
    raw = {
        "summary": "Dentist",
        "location": None,
        "description": "",
        "start": {"dateTime": "2025-01-10T09:00:00", "timeZone": "UTC"},
        "end": {"dateTime": "2025-01-10T09:30:00", "timeZone": "UTC"},
        "id": "evt_123",
    }
    event = Event.from_dict(raw, calendar=cal, owner=Owner.partner)
    assert event.summary == "Dentist"
    assert event.location is None
    assert event.event_id == "evt_123"
    assert event.calendar is cal
    assert event.owner is Owner.partner
    assert event.start.time_zone == "UTC"
