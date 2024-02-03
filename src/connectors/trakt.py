import logging
import os
import time
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path
from time import sleep
from typing import Any, Dict, List

import pytz  # type: ignore
import requests
from requests import Response
from skye_comlib.utils.file import File

from src.models.trakt.episode import ExtendedEpisode
from src.models.trakt.history_item import (
    HistoryItemEpisode,
    HistoryItemExtendedEpisode,
    HistoryItemExtendedMovie,
    HistoryItemMovie,
)
from src.models.trakt.movie import ExtendedMovie, Movie
from src.models.trakt.season import ExtendedSeason
from src.models.trakt.show import Show
from src.models.watch import EpisodeWatch, MovieWatch, Watch


class TraktAPI:
    logging.info("Loading Trakt")

    base_url = "https://api.trakt.tv"
    client_id = os.environ.get("TRAKT_CLIENT_ID", "")
    token = File.read_json(Path("src/credentials/trakt_token.json"))["access_token"]

    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cls.token}",
            "trakt-api-version": "2",
            "trakt-api-key": cls.client_id,
        }

    @classmethod
    def get_request(cls, url: str, params: Dict[str, Any]) -> dict | List[dict]:
        response = requests.get(url, headers=cls.get_headers(), params=params, timeout=60)
        try:
            return response.json()
        except JSONDecodeError:
            raise TraktError(response, url, params)

    @classmethod
    def get_request_paginated(cls, url: str, params: dict, page: int = 1) -> List[dict]:
        params["page"] = page
        response = requests.get(url, headers=cls.get_headers(), params=params, timeout=60)
        try:
            results = response.json()
            if int(response.headers.get("X-Pagination-Page-Count", 1)) > params["page"]:
                results += cls.get_request_paginated(url, params, page + 1)
            return results
        except JSONDecodeError:
            raise TraktError(response, url, params)

    @classmethod
    def post_request(cls, url: str, body: dict) -> dict:
        response = requests.post(url, headers=cls.get_headers(), json=body, timeout=60)
        try:
            return response.json()
        except JSONDecodeError:
            if response.status_code == 429:
                logging.warning("Rate limit exceeded, trying again in 30s.")
                time.sleep(30)
                return cls.post_request(url, body)
            raise TraktError(response, url, body)

    @classmethod
    def get_seasons(cls, show_id: str) -> List[ExtendedSeason]:
        url = f"{cls.base_url}/shows/{show_id}/seasons"
        response = cls.get_request(url, {"extended": "full"})
        return [ExtendedSeason.model_validate(x) for x in response]

    @classmethod
    def get_season_details(cls, show_id: int, season: int) -> List[ExtendedEpisode]:
        url = f"{cls.base_url}/shows/{show_id}/seasons/{season}"
        response = cls.get_request(url, {"extended": "full"})
        return [ExtendedEpisode.model_validate(x) for x in response]

    @classmethod
    def get_episode(cls, show_id: str, season: str, episode: str) -> ExtendedEpisode:
        url = f"{cls.base_url}/shows/{show_id}/seasons/{season}/episodes/{episode}"
        response = cls.get_request(url, {"extended": "full"})
        return ExtendedEpisode.model_validate(response)

    @classmethod
    def get_movie(cls, movie_id: int) -> ExtendedMovie:
        url = f"{cls.base_url}/movies/{movie_id}"
        response = cls.get_request(url, {"extended": "full"})
        return ExtendedMovie.model_validate(response)

    @classmethod
    def search_movie(cls, title: str) -> Movie:
        url = f"{cls.base_url}/search/movie"
        response = cls.get_request(url, {"query": title})
        return Movie.model_validate(response[0]["movie"])

    @classmethod
    def search_show(cls, title: str) -> Show:
        url = f"{cls.base_url}/search/show"
        response = cls.get_request(url, {"query": title})
        return Show.model_validate(response[0]["show"])

    @classmethod
    def get_history_for_episodes(cls, start: datetime, end: datetime) -> List[HistoryItemEpisode]:
        url = f"{cls.base_url}/sync/history/episodes"
        params = {"start_at": start.isoformat() + "Z", "end_at": end.isoformat() + "Z"}
        response = cls.get_request_paginated(url, params)
        return [HistoryItemEpisode.model_validate(x) for x in response]

    @classmethod
    def get_history_for_movies(cls, start: datetime, end: datetime) -> List[HistoryItemMovie]:
        url = f"{cls.base_url}/sync/history/movies"
        params = {"start_at": start.isoformat() + "Z", "end_at": end.isoformat() + "Z"}
        response = cls.get_request_paginated(url, params)
        return [HistoryItemMovie.model_validate(x) for x in response]

    @classmethod
    def get_history_for_episode(cls, episode_id: int) -> List[HistoryItemExtendedEpisode]:
        url = f"{cls.base_url}/sync/history/episodes/{episode_id}"
        response = cls.get_request(url, {"extended": "full"})
        return [HistoryItemExtendedEpisode.model_validate(x) for x in response]

    @classmethod
    def get_history_for_movie(cls, movie_id: int) -> List[HistoryItemExtendedMovie]:
        url = f"{cls.base_url}/sync/history/movies/{movie_id}"
        response = cls.get_request(url, {"extended": "full"})
        return [HistoryItemExtendedMovie.model_validate(x) for x in response]

    @classmethod
    def add_episodes_to_history(cls, watches: List[Watch]) -> dict:
        sleep(2)
        url = f"{cls.base_url}/sync/history"
        body = {
            "movies": [
                {
                    "watched_at": f'{watch.end.astimezone(pytz.timezone("UTC")).isoformat()}Z',
                    "ids": {"trakt": watch.trakt_id},
                }
                for watch in watches
                if isinstance(watch, MovieWatch)
            ],
            "episodes": [
                {
                    "watched_at": f'{watch.end.astimezone(pytz.timezone("UTC")).isoformat()}Z',
                    "ids": {"trakt": watch.episode_id},
                }
                for watch in watches
                if isinstance(watch, EpisodeWatch)
            ],
        }
        return cls.post_request(url, body)

    @classmethod
    def remove_episodes_from_history(cls, watches: List[Watch]) -> dict:
        sleep(2)
        url = f"{cls.base_url}/sync/history/remove"
        body = {
            "movies": [{"ids": {"trakt": watch.trakt_id}} for watch in watches if isinstance(watch, MovieWatch)],
            "episodes": [{"ids": {"trakt": watch.episode_id}} for watch in watches if isinstance(watch, EpisodeWatch)],
        }
        return cls.post_request(url, body)

    @classmethod
    def get_playback(cls, media_type: str = "movie") -> dict:
        url = f"{cls.base_url}/sync/playback/{media_type}"
        response = cls.get_request(url, {})
        if not isinstance(response, dict):
            raise ValueError(f"Expected a dict, got {response}")
        return response


class TraktError(Exception):
    def __init__(self, response: Response, url: str, body: dict):
        error_file = Path(f".logs/.error_{str(datetime.now().timestamp())}.html")

        logging.error(f"Something went wrong. See {error_file} for details.")
        File.write_txt(str(response.text).split("\n"), error_file)
        logging.error("\n".join([f"Body: {body}", f"Url: {url}", f"Status code: {response.status_code}"]))
        super().__init__(f"Could not process Trakt request to {url}.")
