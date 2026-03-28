import pytest

from src.enums.location_category import LocationCategory


@pytest.mark.parametrize(
    "member",
    [
        LocationCategory.HOME,
        LocationCategory.WORK,
        LocationCategory.RESTAURANT,
        LocationCategory.STATION,
        LocationCategory.HOTEL,
        LocationCategory.PARK,
    ],
)
def test_category_values_are_lowercase_snake_strings(member: LocationCategory) -> None:
    assert isinstance(member.value, str)
    assert member.value == member.value.lower()
    assert " " not in member.value


def test_str_enum_behaves_as_string_in_context() -> None:
    assert LocationCategory.CAFE == "cafe"
    assert f"type:{LocationCategory.BAR.value}" == "type:bar"
