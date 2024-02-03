__all__ = ["Movie", "ExtendedMovie"]

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.models.trakt.trakt_ids import TraktIds


class Movie(BaseModel):
    title: str
    year: int
    ids: TraktIds


class ExtendedMovie(Movie):
    tagline: str
    overview: str
    released: date
    runtime: int
    country: str
    updated_at: datetime
    trailer: Optional[str] = Field(None)
    homepage: Optional[str] = Field(None)
    status: str
    rating: float
    votes: int
    comment_count: int
    language: str
    available_translations: List[str]
    genres: List[str]
    certification: Optional[str] = Field(None)
