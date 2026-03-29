import pytest

from src.enums import LocationCategory


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("home", LocationCategory.HOME),
        ("work", LocationCategory.WORK),
        ("restaurant", LocationCategory.RESTAURANT),
        ("station", LocationCategory.STATION),
        ("hotel", LocationCategory.HOTEL),
        ("park", LocationCategory.PARK),
        ("public_square", LocationCategory.PUBLIC_SQUARE),
        ("coffee_bar", LocationCategory.COFFEE_BAR),
    ],
)
def test_from_str(string: str, expected: LocationCategory) -> None:
    assert LocationCategory.from_str(string) is expected


def test_from_str_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unknown LocationCategory"):
        LocationCategory.from_str("unknown_place")


def test_name_lower_roundtrips_from_str() -> None:
    for member in LocationCategory:
        assert LocationCategory.from_str(member.name.lower()) is member


def test_all_members_unique() -> None:
    values = [m.value for m in LocationCategory]
    assert len(values) == len(set(values))
