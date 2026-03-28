from datetime import datetime

from pydantic import BaseModel, Field

from .trakt_ids import TraktIds


class Season(BaseModel):
    number: int
    ids: TraktIds


class ExtendedSeason(Season):
    rating: float
    votes: int
    episode_count: int
    aired_episodes: int
    title: str
    overview: str | None = Field(None)
    first_aired: datetime | None = Field(None)
    updated_at: datetime | None = Field(None)
    network: str
