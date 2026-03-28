import pytest

from src.enums import Owner
from src.models.calendar import Calendar


def test_calendar_get_cal_id() -> None:
    cal = Calendar(name="personal", user="id_c", partner="id_l", shared="id_s")
    assert cal.get_cal_id(Owner.USER) == "id_c"
    assert cal.get_cal_id(Owner.PARTNER) == "id_l"
    assert cal.get_cal_id(Owner.SHARED) == "id_s"


def test_get_calendars_omits_empty_strings() -> None:
    cal = Calendar(name="x", user="only", partner="", shared="")
    ids = cal.get_calendars()
    assert ids == {Owner.USER: "only"}


def test_from_key_success() -> None:
    mapping = {"work": "cal_main", "work_partner": "cal_partner_side", "work_shared": "cal_shared_side"}
    cal = Calendar.from_key("work", mapping)
    assert cal.name == "work"
    assert cal.user == "cal_main"
    assert cal.partner == "cal_partner_side"
    assert cal.shared == "cal_shared_side"


def test_from_key_missing_raises() -> None:
    with pytest.raises(ValueError, match="Key 'missing' not in original dictionary"):
        Calendar.from_key("missing", {"other": "x"})


def test_model_validate_roundtrip() -> None:
    data = {"name": "holidays", "user": "a", "partner": "b", "shared": "c"}
    cal = Calendar.model_validate(data)
    assert cal.model_dump() == data
