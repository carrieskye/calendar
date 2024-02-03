from typing import Tuple


class Point:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self) -> str:
        return f"{self.latitude}, {self.longitude}"

    @staticmethod
    def get_line_through_points(point_a: "Point", point_b: "Point") -> Tuple[float, float]:
        """
        m = (y_2 - y_1) / (x_2 - x_1)
        y = mx + b
        b = -mx + y
        """
        m = (point_a.longitude - point_b.longitude) / (point_a.latitude - point_b.latitude)
        b = -(point_a.latitude * m) + point_a.longitude
        return m, b
