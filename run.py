from datetime import datetime, timedelta

from src.scripts.calendar import Calendar

if __name__ == '__main__':
    calendar = Calendar()
    day = datetime(2019, 10, 1, 4, 0)
    days = 2
    calendar.update_trakt_history(day, day + timedelta(days=days))
