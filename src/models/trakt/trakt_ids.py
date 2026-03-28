from pydantic import BaseModel, Field


class TraktIds(BaseModel):
    trakt: int
    tmdb: int | None = Field(None)
    slug: str | None = Field(None)
    imdb: str | None = Field(None)
    tvdb: int | None = Field(None)
