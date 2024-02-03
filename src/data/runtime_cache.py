from pathlib import Path
from typing import Dict

from skye_comlib.utils.file import File


class RuntimeCache:
    cache_file = Path("data/trakt/cache/runtime.json")
    shows: Dict[str, Dict[str, Dict[str, dict]]]
    movies: Dict[str, int]

    def __init__(self) -> None:
        super().__init__()
        self.load_from_file()

    def add_movie(self, movie_id: int, runtime: int) -> None:
        self.movies[str(movie_id)] = runtime
        self.export_to_file()

    def get_movie(self, movie_id: int) -> int:
        return self.movies[str(movie_id)]

    def add_episode(self, show_id: int, season_no: int, episode_no: int, details: dict) -> None:
        if str(show_id) not in self.shows:
            self.shows[str(show_id)] = {}
        if str(season_no) not in self.shows[str(show_id)]:
            self.shows[str(show_id)][str(season_no)] = {}
        self.shows[str(show_id)][str(season_no)][str(episode_no)] = details
        self.export_to_file()

    def get_episode(self, show_id: int, season_no: int, episode_no: int) -> dict:
        return self.shows[str(show_id)][str(season_no)][str(episode_no)]

    def load_from_file(self) -> None:
        if self.cache_file.exists():
            content = File.read_json(self.cache_file)
            self.shows = content.get("shows", {})
            self.movies = content.get("movies", {})
        else:
            self.shows, self.movies = {}, {}

    def export_to_file(self) -> None:
        File.write_json({"shows": self.shows, "movies": self.movies}, self.cache_file)
