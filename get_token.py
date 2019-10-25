import json
import os
from urllib.parse import urlencode
from uuid import uuid4

import requests
import requests.auth
from flask import Flask, abort, request

REDIRECT_URI = 'http://localhost:3000/trakt_callback'

app = Flask(__name__)


@app.route('/')
def homepage():
    text = '<a href="%s">Authenticate with Trakt</a>'
    return text % make_authorization_url()


@app.route('/trakt_callback')
def trakt_callback():
    error = request.args.get('error', '')
    if error:
        return 'Error: ' + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
        abort(403)
    code = request.args.get('code')
    token = get_token(code)
    with open(f'trakt_token.json', 'w') as file:
        json.dump(token, file, indent='\t')
    return token


def make_authorization_url():
    state = str(uuid4())
    save_created_state(state)

    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'state': state,
        'redirect_uri': REDIRECT_URI,
        'duration': 'temporary'
    }
    return 'https://api.trakt.tv/oauth/authorize?' + urlencode(params)


def save_created_state(state):
    global STATE
    STATE = state


def is_valid_state(state):
    return STATE == state


def get_token(code):
    post_data = {
        'client_id': CLIENT_ID,
        'client_secret': SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post('https://api.trakt.tv/oauth/token', data=post_data)
    return response.json()


if __name__ == '__main__':
    CLIENT_ID = os.environ.get(f'TRAKT_CLIENT_ID')
    SECRET = os.environ.get(f'TRAKT_SECRET')
    app.run(debug=True, port=3000)
