from __future__ import annotations

from geopy import Nominatim

from src.models.point import Point


class BoundingBox:
    def __init__(self, bottom_left: Point, top_left: Point, top_right: Point, bottom_right: Point):
        self.bottom_left = bottom_left
        self.top_left = top_left
        self.top_right = top_right
        self.bottom_right = bottom_right
        self.intersection = self.get_intersection()

    def get_intersection(self):
        """
        m_1 * x + b_1 = m_2 * x + b_2
        m_1 * x - m_2 * x = b_2 - b_1
        (m_1 - m_2) * x = b_2 - b_1
        """
        m_1, b_1 = Point.get_line_through_points(self.top_right, self.bottom_left)
        m_2, b_2 = Point.get_line_through_points(self.bottom_right, self.top_left)

        x = (b_2 - b_1) / (m_1 - m_2)
        y = x * m_1 + b_1
        return Point(x, y)

    def get_address(self):
        geo_locator = Nominatim(user_agent="specify_your_app_name_here")
        return geo_locator.reverse(f"{self.bottom_left.latitude}, {self.bottom_left.longitude}")

    @classmethod
    def deserialise(cls, serialised: dict) -> BoundingBox:
        for key, value in serialised.items():
            serialised[key] = Point.deserialise(value)
        return cls(**serialised)
