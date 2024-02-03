__all__ = ["HistoryItemMovie", "HistoryItemEpisode", "HistoryItemExtendedMovie", "HistoryItemExtendedEpisode"]

from datetime import datetime

from pydantic import BaseModel

from src.models.trakt.episode import Episode, ExtendedEpisode
from src.models.trakt.movie import ExtendedMovie, Movie
from src.models.trakt.show import Show


class HistoryItemBase(BaseModel):
    id: int
    watched_at: datetime
    action: str
    type: str


class HistoryItemMovie(HistoryItemBase):
    movie: Movie


class HistoryItemEpisode(HistoryItemBase):
    episode: Episode
    show: Show


class HistoryItemExtendedMovie(HistoryItemBase):
    movie: ExtendedMovie


class HistoryItemExtendedEpisode(HistoryItemBase):
    episode: ExtendedEpisode
    show: Show
