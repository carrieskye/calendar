import pytest

from src.models import Point


def test_point_str() -> None:
    p = Point(51.5, -0.12)
    assert str(p) == "51.5, -0.12"


def test_line_through_points_diagonal() -> None:
    a = Point(0.0, 0.0)
    b = Point(1.0, 1.0)
    m, b_ = Point.get_line_through_points(a, b)
    assert m == pytest.approx(1.0)
    assert b_ == pytest.approx(0.0)


def test_line_through_points_same_longitude_meridian() -> None:
    a = Point(2.0, 1.0)
    b = Point(5.0, 1.0)
    m, b_ = Point.get_line_through_points(a, b)
    assert m == pytest.approx(0.0)
    assert b_ == pytest.approx(1.0)


def test_line_through_points_same_latitude_raises() -> None:
    a = Point(1.0, 0.0)
    b = Point(1.0, 2.0)
    with pytest.raises(ZeroDivisionError):
        Point.get_line_through_points(a, b)
