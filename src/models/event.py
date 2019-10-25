from src.models.event_datetime import EventDateTime


class Event:

    def __init__(self, summary: str, location: str, description: str, start: EventDateTime, end: EventDateTime):
        self.summary = summary
        self.location = location
        self.description = description
        self.start = start
        self.end = end

    def to_dict(self):
        return {
            'summary': self.summary,
            'location': self.location,
            'description': self.description,
            'start': self.start.to_dict(),
            'end': self.end.to_dict()
        }
