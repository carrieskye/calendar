import json
import os
from datetime import datetime
from typing import List

import requests

from src.models.watch import EpisodeWatch, Watch, MovieWatch


class TraktAPI:

    def __init__(self):
        self.base_url = 'https://api.trakt.tv'
        self.client_id = os.environ.get('TRAKT_CLIENT_ID')
        with open('src/credentials/trakt_token.json', 'r') as file:
            self.token = json.load(file).get('access_token')

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}',
            'trakt-api-version': '2',
            'trakt-api-key': self.client_id
        }

    def get_request(self, url, params):
        response = requests.get(url, headers=self.get_headers(), params=params)
        return response.json()

    def get_request_paginated(self, url, params, page=1):
        params['page'] = page
        response = requests.get(url, headers=self.get_headers(), params=params)
        results = response.json()
        if int(response.headers.get('X-Pagination-Page-Count')) > params['page']:
            results += self.get_request_paginated(url, params, page + 1)
        return results

    def post_request(self, url, body):
        response = requests.post(url, headers=self.get_headers(), json=body)
        return response.json()

    def get_show_details(self, title):
        url = f'{self.base_url}/search/show'
        response = self.get_request(url, {'query': title})
        return response[0]['show']

    def get_seasons(self, show_id):
        url = f'{self.base_url}/shows/{show_id}/seasons'
        return self.get_request(url, {'extended': 'full'})

    def get_season_details(self, show_id, season):
        url = f'{self.base_url}/shows/{show_id}/seasons/{season}'
        return self.get_request(url, {'extended': 'full'})

    def get_episode(self, show_id, season, episode):
        url = f'{self.base_url}/shows/{show_id}/seasons/{season}/episodes/{episode}'
        return self.get_request(url, {'extended': 'full'})

    def get_movie(self, movie_id):
        url = f'{self.base_url}/movies/{movie_id}'
        return self.get_request(url, {'extended': 'full'})

    def get_history(self, start: datetime, end: datetime):
        url = f'{self.base_url}/sync/history'
        params = {'start_at': start.isoformat() + 'Z', 'end_at': end.isoformat() + 'Z'}
        return self.get_request_paginated(url, params)

    def get_history_for_episode(self, episode_id: str):
        url = f'{self.base_url}/sync/history/episodes/{episode_id}'
        return self.get_request(url, {'extended': 'full'})

    def add_episodes_to_history(self, watches: List[Watch]):
        url = f'{self.base_url}/sync/history'
        body = {
            'movies': [{
                'watched_at': watch.end.isoformat() + 'Z',
                'ids': {'trakt': watch.trakt_id}
            } for watch in watches if isinstance(watch, MovieWatch)],
            'episodes': [{
                'watched_at': watch.end.isoformat() + 'Z',
                'ids': {'trakt': watch.episode_id}
            } for watch in watches if isinstance(watch, EpisodeWatch)]
        }
        return self.post_request(url, body)

    def remove_episodes_from_history(self, watches: List[Watch]):
        url = f'{self.base_url}/sync/history/remove'
        body = {
            'movies': [{
                'ids': {'trakt': watch.trakt_id}
            } for watch in watches if isinstance(watch, MovieWatch)],
            'episodes': [{
                'ids': {'trakt': watch.episode_id}
            } for watch in watches if isinstance(watch, EpisodeWatch)]
        }
        return self.post_request(url, body)
