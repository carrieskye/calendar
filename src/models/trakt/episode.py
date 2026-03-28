from datetime import datetime

from pydantic import BaseModel

from .trakt_ids import TraktIds


class Episode(BaseModel):
    season: int
    number: int
    title: str
    ids: TraktIds


class ExtendedEpisode(Episode):
    number_abs: int | None
    overview: str | None
    first_aired: datetime | None
    updated_at: datetime
    rating: float
    votes: int
    comment_count: int
    available_translations: list[str]
    runtime: int
    episode_type: str
