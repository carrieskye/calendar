__all__ = ["Show"]

from pydantic import BaseModel

from src.models.trakt.trakt_ids import TraktIds


class Show(BaseModel):
    title: str
    year: int
    ids: TraktIds
