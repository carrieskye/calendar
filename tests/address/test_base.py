"""Generic Address parsing helpers."""

import pytest

from src.models.location.address import Address


@pytest.mark.parametrize(
    ("line", "expected_postal", "expected_city"),
    [
        ("12345 Berlin", "12345", "Berlin"),
        ("10115 Berlin", "10115", "Berlin"),
    ],
)
def test_parse_city_and_postal_code_postal_first(line: str, expected_postal: str, expected_city: str) -> None:
    out = Address.parse_city_and_postal_code(line)
    assert out["postal_code"] == expected_postal
    assert out["city"] == expected_city


@pytest.mark.parametrize(
    ("line", "expected_city", "expected_postal"),
    [
        ("Berlin 12345", "Berlin", "12345"),
        ("München 80331", "München", "80331"),
    ],
)
def test_parse_city_and_postal_code_city_first(line: str, expected_city: str, expected_postal: str) -> None:
    out = Address.parse_city_and_postal_code(line)
    assert out["city"] == expected_city
    assert out["postal_code"] == expected_postal


def test_parse_city_and_postal_code_no_match_returns_city_only() -> None:
    out = Address.parse_city_and_postal_code("Paris")
    assert out["postal_code"] == ""
    assert out["city"] == "Paris"


def test_parse_city_and_postal_code_multi_digit_postal() -> None:
    out = Address.parse_city_and_postal_code("12345 678 MainTown")
    assert out["postal_code"] == "12345 678"
    assert out["city"] == "MainTown"


def test_parse_other_parts_house_number_trailing() -> None:
    out = Address.parse_other_parts(["Org", "Main St 42"])
    assert out["address_lines"] == ["Org"]
    assert out["street"] == "Main St"
    assert out["house_no"] == "42"


def test_parse_other_parts_house_number_leading() -> None:
    out = Address.parse_other_parts(["42 Main St"])
    assert out["address_lines"] == []
    assert out["street"] == "Main St"
    assert out["house_no"] == "42"


def test_parse_other_parts_empty_list() -> None:
    out = Address.parse_other_parts([])
    assert out["address_lines"] == []
    assert out["street"] == ""
    assert out["house_no"] == ""


def test_parse_other_parts_no_house_number() -> None:
    out = Address.parse_other_parts(["Building A", "Main Street"])
    assert out["address_lines"] == ["Building A", "Main Street"]
    assert out["street"] == ""
    assert out["house_no"] == ""
