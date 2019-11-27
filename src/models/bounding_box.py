from src.models.point import Point


class BoundingBox:

    def __init__(self, bottom_left: Point, top_left: Point, top_right: Point, bottom_right: Point, intersection: Point):
        self.bottom_left = bottom_left
        self.top_left = top_left
        self.top_right = top_right
        self.bottom_right = bottom_right
        self.intersection = intersection

    def serialise(self):
        return {
            'bottom_left': self.bottom_left.serialise(),
            'top_left': self.top_left.serialise(),
            'top_right': self.top_right.serialise(),
            'bottom_right': self.bottom_right.serialise(),
            'intersection': self.intersection.serialise()
        }

    @staticmethod
    def deserialise(serialised: dict):
        for key, value in serialised.items():
            serialised[key] = Point.deserialise(value)
        return BoundingBox(**serialised)
