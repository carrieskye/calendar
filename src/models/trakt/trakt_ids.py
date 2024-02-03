__all__ = ["TraktIds"]

from typing import Optional

from pydantic import BaseModel, Field


class TraktIds(BaseModel):
    trakt: int
    tmdb: Optional[int] = Field(None)
    slug: Optional[str] = Field(None)
    imdb: Optional[str] = Field(None)
    tvdb: Optional[int] = Field(None)
