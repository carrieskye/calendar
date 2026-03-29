import pytest

from src.address_parser import AddressParser
from src.models.location.address import DEAddress, UKAddress


def test_uk_cardiff_full_string() -> None:
    raw = "1 Sample St, Cardiff CF10 1AB, United Kingdom"
    addr = AddressParser.run(raw)
    assert isinstance(addr, UKAddress)
    assert addr.city == "Cardiff"
    assert addr.postal_code == "CF10 1AB"
    assert addr.street == "Sample St"
    assert addr.house_no == "1"
    assert addr.country_code == "UK"


@pytest.mark.parametrize(
    "raw",
    [
        "1 Sample St, Cardiff CF10 1AB, United Kingdom",
        "1 Sample St, Cardiff CF10 1AB, UK",
    ],
)
def test_uk_accepts_united_kingdom_or_uk_suffix(raw: str) -> None:
    addr = AddressParser.run(raw)
    assert isinstance(addr, UKAddress)
    assert addr.city == "Cardiff"


def test_germany_de_address() -> None:
    raw = "Musterstraße 1, 10115 Berlin, Germany"
    addr = AddressParser.run(raw)
    assert isinstance(addr, DEAddress)
    assert addr.country_code == "DE"
    assert addr.city == "Berlin"
    assert addr.postal_code == "10115"
    assert addr.street == "Musterstraße"
    assert addr.house_no == "1"


def test_unknown_country_raises_lookup_error() -> None:
    with pytest.raises(LookupError):
        AddressParser.run("Somewhere, NoSuchCountryName")


def test_supported_country_not_in_parser_lookup_raises_key_error() -> None:
    """United States resolves in pycountry but has no Address subclass."""
    with pytest.raises(KeyError):
        AddressParser.run("123 Main St, New York 10001, United States")
