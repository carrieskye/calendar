from src.models.address import Address


class FrequentLocation:

    def __init__(self, title: str, latitude, longitude, radius: int, address: Address, category: str):
        self.title = title
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.radius = int(radius)
        self.address = address
        self.category = category
