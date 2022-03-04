import logging
import os
import time
from datetime import datetime
from json import JSONDecodeError
from typing import List

import pytz
import requests
from requests import Response
from skye_comlib.utils.file import File
from skye_comlib.utils.logger import Logger

from src.models.watch import EpisodeWatch, Watch, MovieWatch


class TraktAPI:
    logging.info("Loading Trakt")

    base_url = "https://api.trakt.tv"
    client_id = os.environ.get("TRAKT_CLIENT_ID")
    token = File.read_json("src/credentials/trakt_token.json")["access_token"]

    @classmethod
    def get_headers(cls):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cls.token}",
            "trakt-api-version": "2",
            "trakt-api-key": cls.client_id,
        }

    @classmethod
    def get_request(cls, url, params) -> dict:
        response = requests.get(url, headers=cls.get_headers(), params=params)
        try:
            return response.json()
        except JSONDecodeError:
            raise TraktException(response, url, params)

    @classmethod
    def get_request_paginated(cls, url, params, page=1):
        params["page"] = page
        response = requests.get(url, headers=cls.get_headers(), params=params)
        try:
            results = response.json()
            if int(response.headers.get("X-Pagination-Page-Count")) > params["page"]:
                results += cls.get_request_paginated(url, params, page + 1)
            return results
        except JSONDecodeError:
            raise TraktException(response, url, params)

    @classmethod
    def post_request(cls, url, body) -> dict:
        response = requests.post(url, headers=cls.get_headers(), json=body)
        try:
            return response.json()
        except JSONDecodeError:
            if response.status_code == 429:
                Logger.log("Rate limit exceeded, trying again in 30s.")
                time.sleep(30)
                return cls.post_request(url, body)
            raise TraktException(response, url, body)

    @classmethod
    def get_show_details(cls, title):
        url = f"{cls.base_url}/search/show"
        response = cls.get_request(url, {"query": title})
        return response[0]["show"]

    @classmethod
    def get_seasons(cls, show_id):
        url = f"{cls.base_url}/shows/{show_id}/seasons"
        return cls.get_request(url, {"extended": "full"})

    @classmethod
    def get_season_details(cls, show_id, season):
        url = f"{cls.base_url}/shows/{show_id}/seasons/{season}"
        return cls.get_request(url, {"extended": "full"})

    @classmethod
    def get_episode(cls, show_id, season, episode):
        url = f"{cls.base_url}/shows/{show_id}/seasons/{season}/episodes/{episode}"
        return cls.get_request(url, {"extended": "full"})

    @classmethod
    def get_movie(cls, movie_id):
        url = f"{cls.base_url}/movies/{movie_id}"
        return cls.get_request(url, {"extended": "full"})

    @classmethod
    def search_movie(cls, title):
        url = f"{cls.base_url}/search/movie"
        response = cls.get_request(url, {"query": title})
        return response[0]["movie"]

    @classmethod
    def get_history(cls, start: datetime, end: datetime):
        url = f"{cls.base_url}/sync/history"
        params = {"start_at": start.isoformat() + "Z", "end_at": end.isoformat() + "Z"}
        return cls.get_request_paginated(url, params)

    @classmethod
    def get_history_for_episode(cls, episode_id: str):
        url = f"{cls.base_url}/sync/history/episodes/{episode_id}"
        return cls.get_request(url, {"extended": "full"})

    @classmethod
    def get_history_for_movie(cls, movie_id: str):
        url = f"{cls.base_url}/sync/history/movies/{movie_id}"
        return cls.get_request(url, {"extended": "full"})

    @classmethod
    def add_episodes_to_history(cls, watches: List[Watch]):
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
    def remove_episodes_from_history(cls, watches: List[Watch]):
        url = f"{cls.base_url}/sync/history/remove"
        body = {
            "movies": [
                {"ids": {"trakt": watch.trakt_id}}
                for watch in watches
                if isinstance(watch, MovieWatch)
            ],
            "episodes": [
                {"ids": {"trakt": watch.episode_id}}
                for watch in watches
                if isinstance(watch, EpisodeWatch)
            ],
        }
        return cls.post_request(url, body)

    @classmethod
    def get_playback(cls, media_type: str = "movie"):
        url = f"{cls.base_url}/sync/playback/{media_type}"
        return cls.get_request(url, {})


class TraktException(Exception):
    def __init__(self, response: Response, url: str, body: dict):
        error_file = f".logs/.error_{str(datetime.now().timestamp())}.html"

        Logger.log(f"\n Something went wrong. See {error_file} for details.")
        File.write_txt(str(response.text).split("\n"), error_file, log=False)
        Logger.log(
            "\n".join(
                [f"Body: {body}", f"Url: {url}", f"Status code: {response.status_code}"]
            )
        )
        super().__init__(f"Could not process Trakt request to {url}.")
