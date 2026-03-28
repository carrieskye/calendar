import pytest

from src.models.calendar import Calendar, Owner


def test_calendar_get_cal_id() -> None:
    cal = Calendar(name="personal", carrie="id_c", larry="id_l", shared="id_s")
    assert cal.get_cal_id(Owner.carrie) == "id_c"
    assert cal.get_cal_id(Owner.larry) == "id_l"
    assert cal.get_cal_id(Owner.shared) == "id_s"


def test_get_calendars_omits_empty_strings() -> None:
    cal = Calendar(name="x", carrie="only", larry="", shared="")
    ids = cal.get_calendars()
    assert ids == {Owner.carrie: "only"}


def test_from_key_success() -> None:
    mapping = {"work": "cal_main", "work_larry": "cal_larry_side", "work_shared": "cal_shared_side"}
    cal = Calendar.from_key("work", mapping)
    assert cal.name == "work"
    assert cal.carrie == "cal_main"
    assert cal.larry == "cal_larry_side"
    assert cal.shared == "cal_shared_side"


def test_from_key_missing_raises() -> None:
    with pytest.raises(ValueError, match="Key 'missing' not in original dictionary"):
        Calendar.from_key("missing", {"other": "x"})


def test_model_validate_roundtrip() -> None:
    data = {"name": "holidays", "carrie": "a", "larry": "b", "shared": "c"}
    cal = Calendar.model_validate(data)
    assert cal.model_dump() == data
