from datetime import datetime

import pytest

from src.enums import LocationCategory
from src.models.location.address import UKAddress
from src.models.location.bounding_box import BoundingBox
from src.models.location.geo_location import GeoLocation
from src.models.location_timestamp import LocationTimestamp

# ── helpers ───────────────────────────────────────────────────────────────────


def _make_geo_location(bounding_box: BoundingBox | None = None) -> GeoLocation:
    return GeoLocation(
        time_zone="Europe/London",
        category=LocationCategory.HOME,
        label="home",
        short="Home",
        address=UKAddress(original="1 Example Street, Cardiff, CF10 1AA, United Kingdom"),
        bounding_box=bounding_box,
    )


def _make_timestamp(latitude: float, longitude: float) -> LocationTimestamp:
    return LocationTimestamp(
        date_time=datetime(2024, 1, 1, 12),
        latitude=latitude,
        longitude=longitude,
        accuracy=10,
    )


def _make_box() -> BoundingBox:
    return BoundingBox(min_latitude=51.4, max_latitude=51.6, min_longitude=-3.3, max_longitude=-3.1)


# ── within_bounding_box: no bounding box ─────────────────────────────────────


def test_within_bounding_box_no_box_returns_false() -> None:
    geo = _make_geo_location()
    ts = _make_timestamp(51.5, -3.2)
    assert geo.within_bounding_box(ts) is False


# ── within_bounding_box: point inside ────────────────────────────────────────


def test_within_bounding_box_point_inside_returns_true() -> None:
    geo = _make_geo_location(bounding_box=_make_box())
    ts = _make_timestamp(51.5, -3.2)
    assert geo.within_bounding_box(ts) is True


# ── within_bounding_box: point on boundary ───────────────────────────────────


def test_within_bounding_box_point_on_min_boundary() -> None:
    geo = _make_geo_location(bounding_box=_make_box())
    ts = _make_timestamp(51.4, -3.3)
    assert geo.within_bounding_box(ts) is True


def test_within_bounding_box_point_on_max_boundary() -> None:
    geo = _make_geo_location(bounding_box=_make_box())
    ts = _make_timestamp(51.6, -3.1)
    assert geo.within_bounding_box(ts) is True


# ── within_bounding_box: point outside ───────────────────────────────────────


def test_within_bounding_box_point_outside_latitude() -> None:
    geo = _make_geo_location(bounding_box=_make_box())
    ts = _make_timestamp(52.0, -3.2)
    assert geo.within_bounding_box(ts) is False


def test_within_bounding_box_point_outside_longitude() -> None:
    geo = _make_geo_location(bounding_box=_make_box())
    ts = _make_timestamp(51.5, -4.0)
    assert geo.within_bounding_box(ts) is False


# ── serialisation round-trip ──────────────────────────────────────────────────


def test_to_dict_with_bounding_box_includes_all_keys() -> None:
    geo = _make_geo_location(bounding_box=_make_box())
    d = geo.to_dict()
    assert d["min_latitude"] == 51.4
    assert d["max_latitude"] == 51.6
    assert d["min_longitude"] == -3.3
    assert d["max_longitude"] == -3.1


def test_to_dict_without_bounding_box_has_empty_strings() -> None:
    geo = _make_geo_location()
    d = geo.to_dict()
    assert d["min_latitude"] == ""
    assert d["max_latitude"] == ""
    assert d["min_longitude"] == ""
    assert d["max_longitude"] == ""


def test_round_trip_with_bounding_box() -> None:
    """to_dict() output can be passed back to GeoLocation() to reconstruct the model."""
    original = _make_geo_location(bounding_box=_make_box())
    d = original.to_dict()
    reconstructed = GeoLocation(**d)
    assert reconstructed.bounding_box is not None
    assert reconstructed.bounding_box.min_latitude == pytest.approx(51.4)
    assert reconstructed.bounding_box.max_latitude == pytest.approx(51.6)
    assert reconstructed.bounding_box.min_longitude == pytest.approx(-3.3)
    assert reconstructed.bounding_box.max_longitude == pytest.approx(-3.1)


def test_round_trip_without_bounding_box() -> None:
    """to_dict() output without a bounding box reconstructs with bounding_box=None."""
    original = _make_geo_location()
    d = original.to_dict()
    reconstructed = GeoLocation(**d)
    assert reconstructed.bounding_box is None


# ── CSV row parsing ───────────────────────────────────────────────────────────


def test_from_csv_row_with_bounding_box_columns() -> None:
    """CSV rows with all four bounding box columns are parsed into a BoundingBox."""
    row = {
        "time_zone": "Europe/London",
        "category": "home",
        "label": "home",
        "short": "Home",
        "address": "1 Example Street, Cardiff, CF10 1AA, United Kingdom",
        "min_latitude": "51.4",
        "max_latitude": "51.6",
        "min_longitude": "-3.3",
        "max_longitude": "-3.1",
    }
    geo = GeoLocation(**row)
    assert geo.bounding_box is not None
    assert geo.bounding_box.min_latitude == pytest.approx(51.4)


def test_from_csv_row_without_bounding_box_columns() -> None:
    """CSV rows without bounding box columns (older format) produce bounding_box=None."""
    row = {
        "time_zone": "Europe/London",
        "category": "home",
        "label": "home",
        "short": "Home",
        "address": "1 Example Street, Cardiff, CF10 1AA, United Kingdom",
    }
    geo = GeoLocation(**row)
    assert geo.bounding_box is None


def test_from_csv_row_with_empty_bounding_box_columns() -> None:
    """CSV rows with empty bounding box values (no box set) produce bounding_box=None."""
    row = {
        "time_zone": "Europe/London",
        "category": "home",
        "label": "home",
        "short": "Home",
        "address": "1 Example Street, Cardiff, CF10 1AA, United Kingdom",
        "min_latitude": "",
        "max_latitude": "",
        "min_longitude": "",
        "max_longitude": "",
    }
    geo = GeoLocation(**row)
    assert geo.bounding_box is None
