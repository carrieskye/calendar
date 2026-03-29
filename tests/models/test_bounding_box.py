import pytest

from src.models import BoundingBox, Point


def _box() -> BoundingBox:
    return BoundingBox(min_latitude=51.0, max_latitude=52.0, min_longitude=-3.0, max_longitude=-2.0)


# ── intersection ─────────────────────────────────────────────────────────────


def test_intersection_is_center() -> None:
    box = _box()
    center = box.intersection
    assert isinstance(center, Point)
    assert center.latitude == pytest.approx(51.5)
    assert center.longitude == pytest.approx(-2.5)


def test_intersection_non_symmetric_box() -> None:
    box = BoundingBox(min_latitude=10.0, max_latitude=30.0, min_longitude=5.0, max_longitude=25.0)
    center = box.intersection
    assert center.latitude == pytest.approx(20.0)
    assert center.longitude == pytest.approx(15.0)


# ── contains ─────────────────────────────────────────────────────────────────


def test_contains_point_inside() -> None:
    assert _box().contains(51.5, -2.5)


def test_contains_point_outside_latitude() -> None:
    assert not _box().contains(53.0, -2.5)


def test_contains_point_outside_longitude() -> None:
    assert not _box().contains(51.5, -4.0)


def test_contains_point_on_min_boundary() -> None:
    assert _box().contains(51.0, -3.0)


def test_contains_point_on_max_boundary() -> None:
    assert _box().contains(52.0, -2.0)


def test_contains_point_exactly_outside_boundary() -> None:
    assert not _box().contains(52.0001, -2.0)


# ── validation ────────────────────────────────────────────────────────────────


def test_invalid_latitude_range_raises() -> None:
    with pytest.raises(ValueError, match="min_latitude"):
        BoundingBox(min_latitude=53.0, max_latitude=51.0, min_longitude=-3.0, max_longitude=-2.0)


def test_invalid_longitude_range_raises() -> None:
    with pytest.raises(ValueError, match="min_longitude"):
        BoundingBox(min_latitude=51.0, max_latitude=52.0, min_longitude=-2.0, max_longitude=-3.0)


def test_equal_latitude_bounds_valid() -> None:
    """A box with equal min/max latitude is a horizontal line — still valid."""
    box = BoundingBox(min_latitude=51.5, max_latitude=51.5, min_longitude=-3.0, max_longitude=-2.0)
    assert box.contains(51.5, -2.5)
    assert not box.contains(51.6, -2.5)
