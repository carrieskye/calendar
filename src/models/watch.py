from datetime import datetime
from typing import Dict, Optional

from dateutil.relativedelta import relativedelta  # type: ignore
from pydantic import BaseModel, Field

from src.models.trakt.history_item import (
    HistoryItemEpisode,
    HistoryItemExtendedEpisode,
    HistoryItemExtendedMovie,
    HistoryItemMovie,
)


class TempEpisodeWatch(BaseModel):
    watched_at: datetime
    show_id: int
    show_title: str
    season_no: int
    episode_no: int
    episode_id: int
    episode_title: Optional[str] = Field(None)
    slug: Optional[str] = Field(None)

    @classmethod
    def from_result(cls, result: HistoryItemEpisode | HistoryItemExtendedEpisode) -> "TempEpisodeWatch":
        return cls(
            watched_at=result.watched_at,
            show_id=result.show.ids.trakt,
            show_title=result.show.title,
            season_no=result.episode.season,
            episode_no=result.episode.number,
            episode_id=result.episode.ids.trakt,
            episode_title=result.episode.title,
            slug=result.show.ids.slug,
        )


class TempMovieWatch(BaseModel):
    watched_at: datetime
    movie_id: int
    movie_title: str
    slug: str
    year: int

    @classmethod
    def from_result(cls, result: HistoryItemMovie | HistoryItemExtendedMovie) -> "TempMovieWatch":
        return cls(
            watched_at=result.watched_at,
            movie_id=result.movie.ids.trakt,
            movie_title=result.movie.title,
            slug=result.movie.ids.slug,
            year=result.movie.year,
        )


class Watch:
    def __init__(self, trakt_id: int, title: str, details: dict, watched_at: datetime, runtime: int):
        self.trakt_id = trakt_id
        self.title = title
        self.details = details
        self.end = watched_at
        self.runtime = runtime

    def __str__(self) -> str:
        return self.title

    def get_start(self) -> datetime:
        return self.end - relativedelta(minutes=self.runtime)


class EpisodeWatch(Watch):
    def __init__(self, temp_watch: TempEpisodeWatch, runtime: int):
        self.show_title = temp_watch.show_title
        self.season_no = temp_watch.season_no
        self.episode_id = temp_watch.episode_id
        self.episode_title = temp_watch.episode_title
        self.episode_no = temp_watch.episode_no
        self.slug = temp_watch.slug

        show_id = temp_watch.show_id
        show_title = self.show_title.replace("Marvel's ", "").split(" (")[0]
        watched_at = temp_watch.watched_at
        details = {
            "url": f"https://trakt.tv/shows/{self.slug}/seasons/{self.season_no}/episodes/{self.episode_no}",
            "episode": f'S{str(self.season_no).rjust(2, "0")}E{str(self.episode_no).rjust(2, "0")}',
        }
        super().__init__(show_id, show_title, details, watched_at, runtime)

    def __str__(self) -> str:
        return f'{self.title} ({self.details["episode"]})'

    def get_export_dict(self) -> dict:
        return {
            "season": self.season_no,
            "episode": self.episode_no,
            "title": self.episode_title,
            "start": self.get_start().strftime("%Y-%m-%d %H:%M:%S"),
            "end": self.end.strftime("%Y-%m-%d %H:%M:%S"),
        }


class MovieWatch(Watch):
    def __init__(self, temp_watch: TempMovieWatch, runtime: int):
        self.movie_title = temp_watch.movie_title
        self.slug = temp_watch.slug
        self.year = temp_watch.year

        movie_id = temp_watch.movie_id
        watched_at = temp_watch.watched_at
        details = {"url": f"https://trakt.tv/movies/{self.slug}", "year": self.year}
        Watch.__init__(self, movie_id, self.movie_title, details, watched_at, runtime)

    def __str__(self) -> str:
        return f"{self.title} ({self.year})"

    def get_export_dict(self) -> Dict[str, str | int]:
        return {
            "title": self.movie_title,
            "year": self.year,
            "start": self.get_start().strftime("%Y-%m-%d %H:%M:%S"),
            "end": self.end.strftime("%Y-%m-%d %H:%M:%S"),
        }
