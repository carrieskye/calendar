"""UK-specific address line parsing."""

import pytest

from src.models.location.address import UKAddress


@pytest.mark.parametrize(
    ("line", "city", "postal"),
    [
        ("Cardiff CF10 1AB", "Cardiff", "CF10 1AB"),
        ("London SW1A 2AA", "London", "SW1A 2AA"),
        ("Bristol BS1 5TR", "Bristol", "BS1 5TR"),
    ],
)
def test_parse_city_and_postal_code_standard_uk(line: str, city: str, postal: str) -> None:
    out = UKAddress.parse_city_and_postal_code(line)
    assert out["city"] == city
    assert out["postal_code"] == postal


def test_parse_city_and_postal_code_no_match_falls_back() -> None:
    out = UKAddress.parse_city_and_postal_code("UnknownFormat")
    assert out["postal_code"] == ""
    assert out["city"] == "UnknownFormat"


def test_parse_other_parts_simple_street_with_house_number() -> None:
    out = UKAddress.parse_other_parts(["1 Sample St"])
    assert out["house_no"] == "1"
    assert out["street"] == "Sample St"
    assert out["district"] == ""


def test_parse_other_parts_street_with_road_abbreviation() -> None:
    out = UKAddress.parse_other_parts(["10 High St"])
    assert out["house_no"] == "10"
    assert out["street"] == "High St"


def test_parse_other_parts_multiline_before_numbered_street() -> None:
    """Lines before the numbered street become address_lines (e.g. venue + unit)."""
    out = UKAddress.parse_other_parts(["Tramshed Tech", "Unit D", "9 Pendyris St"])
    assert out["address_lines"] == ["Tramshed Tech", "Unit D"]
    assert out["house_no"] == "9"
    assert out["street"] == "Pendyris St"


def test_parse_other_parts_two_separate_numbered_streets_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        UKAddress.parse_other_parts(["10 Downing St", "Middle", "20 Baker St"])
