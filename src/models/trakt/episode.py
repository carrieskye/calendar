__all__ = ["Episode", "ExtendedEpisode"]

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.models.trakt.trakt_ids import TraktIds


class Episode(BaseModel):
    season: int
    number: int
    title: str
    ids: TraktIds


class ExtendedEpisode(Episode):
    number_abs: Optional[int]
    overview: Optional[str]
    first_aired: Optional[datetime]
    updated_at: datetime
    rating: float
    votes: int
    comment_count: int
    available_translations: List[str]
    runtime: int
    episode_type: str
