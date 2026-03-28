from pydantic import BaseModel

from .trakt_ids import TraktIds


class Show(BaseModel):
    title: str
    year: int
    ids: TraktIds
