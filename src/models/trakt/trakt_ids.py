from pydantic import BaseModel, Field


class TraktIds(BaseModel):
    trakt: int
    tmdb: int | None = Field(default=None)
    slug: str | None = Field(default=None)
    imdb: str | None = Field(default=None)
    tvdb: int | None = Field(default=None)
