class Point:

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def serialise(self):
        return self.__dict__

    @staticmethod
    def deserialise(serialised: dict):
        return Point(**serialised)
