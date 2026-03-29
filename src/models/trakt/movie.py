from datetime import date, datetime

from pydantic import BaseModel, Field

from .trakt_ids import TraktIds


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
    trailer: str | None = Field(default=None)
    homepage: str | None = Field(default=None)
    status: str
    rating: float
    votes: int
    comment_count: int
    language: str
    available_translations: list[str]
    genres: list[str]
    certification: str | None = Field(default=None)
