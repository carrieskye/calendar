__all__ = ["Season", "ExtendedSeason"]

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.models.trakt.trakt_ids import TraktIds


class Season(BaseModel):
    number: int
    ids: TraktIds


class ExtendedSeason(Season):
    rating: float
    votes: int
    episode_count: int
    aired_episodes: int
    title: str
    overview: Optional[str] = Field(None)
    first_aired: Optional[datetime] = Field(None)
    updated_at: Optional[datetime] = Field(None)
    network: str
