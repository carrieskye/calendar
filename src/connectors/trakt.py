import os
from datetime import datetime
from typing import List

import pytz
import requests

from src.models.watch import EpisodeWatch, Watch, MovieWatch
from src.utils.utils import Utils


class TraktAPI:
    base_url = 'https://api.trakt.tv'
    client_id = os.environ.get('TRAKT_CLIENT_ID')
    token = Utils.read_json('src/credentials/trakt_token.json')['access_token']

    @classmethod
    def get_headers(cls):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {cls.token}',
            'trakt-api-version': '2',
            'trakt-api-key': cls.client_id
        }

    @classmethod
    def get_request(cls, url, params):
        response = requests.get(url, headers=cls.get_headers(), params=params)
        return response.json()

    @classmethod
    def get_request_paginated(cls, url, params, page=1):
        params['page'] = page
        response = requests.get(url, headers=cls.get_headers(), params=params)
        results = response.json()
        if int(response.headers.get('X-Pagination-Page-Count')) > params['page']:
            results += cls.get_request_paginated(url, params, page + 1)
        return results

    @classmethod
    def post_request(cls, url, body):
        response = requests.post(url, headers=cls.get_headers(), json=body)
        return response.json()

    @classmethod
    def get_show_details(cls, title):
        url = f'{cls.base_url}/search/show'
        response = cls.get_request(url, {'query': title})
        return response[0]['show']

    @classmethod
    def get_seasons(cls, show_id):
        url = f'{cls.base_url}/shows/{show_id}/seasons'
        return cls.get_request(url, {'extended': 'full'})

    @classmethod
    def get_season_details(cls, show_id, season):
        url = f'{cls.base_url}/shows/{show_id}/seasons/{season}'
        return cls.get_request(url, {'extended': 'full'})

    @classmethod
    def get_episode(cls, show_id, season, episode):
        url = f'{cls.base_url}/shows/{show_id}/seasons/{season}/episodes/{episode}'
        return cls.get_request(url, {'extended': 'full'})

    @classmethod
    def get_movie(cls, movie_id):
        url = f'{cls.base_url}/movies/{movie_id}'
        return cls.get_request(url, {'extended': 'full'})

    @classmethod
    def get_history(cls, start: datetime, end: datetime):
        url = f'{cls.base_url}/sync/history'
        params = {'start_at': start.isoformat() + 'Z', 'end_at': end.isoformat() + 'Z'}
        return cls.get_request_paginated(url, params)

    @classmethod
    def get_history_for_episode(cls, episode_id: str):
        url = f'{cls.base_url}/sync/history/episodes/{episode_id}'
        return cls.get_request(url, {'extended': 'full'})

    @classmethod
    def add_episodes_to_history(cls, watches: List[Watch]):
        url = f'{cls.base_url}/sync/history'
        body = {
            'movies': [{
                'watched_at': watch.end.astimezone(pytz.timezone('UTC')).isoformat() + 'Z',
                'ids': {'trakt': watch.trakt_id}
            } for watch in watches if isinstance(watch, MovieWatch)],
            'episodes': [{
                'watched_at': watch.end.astimezone(pytz.timezone('UTC')).isoformat() + 'Z',
                'ids': {'trakt': watch.episode_id}
            } for watch in watches if isinstance(watch, EpisodeWatch)]
        }
        return cls.post_request(url, body)

    @classmethod
    def remove_episodes_from_history(cls, watches: List[Watch]):
        url = f'{cls.base_url}/sync/history/remove'
        body = {
            'movies': [{
                'ids': {'trakt': watch.trakt_id}
            } for watch in watches if isinstance(watch, MovieWatch)],
            'episodes': [{
                'ids': {'trakt': watch.episode_id}
            } for watch in watches if isinstance(watch, EpisodeWatch)]
        }
        return cls.post_request(url, body)
