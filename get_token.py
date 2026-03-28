import json
import os
import sys
from urllib.parse import urlencode
from uuid import uuid4

try:
    import requests
    from flask import Flask, abort, request
    from flask.typing import ResponseReturnValue
except ModuleNotFoundError as exc:
    print(
        f"Missing dependency {exc.name!r}. Use the project virtualenv, e.g.\n"
        "  pipenv install\n"
        "  pipenv run python get_token.py",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc

REDIRECT_URI = "http://localhost:3000/trakt_callback"

app = Flask(__name__)
STATE = ""

CLIENT_ID = os.environ.get("TRAKT_CLIENT_ID")
SECRET = os.environ.get("TRAKT_SECRET")

if not CLIENT_ID or not SECRET:
    raise RuntimeError("Missing env vars: TRAKT_CLIENT_ID and/or TRAKT_SECRET")


@app.route("/")
def homepage() -> str:
    return f'<a href="{make_authorization_url()}">Authenticate with Trakt</a>'


@app.route("/trakt_callback")
def trakt_callback() -> ResponseReturnValue:
    error = request.args.get("error", "")
    if error:
        return "Error: " + error, 400

    state = request.args.get("state", "")
    if not is_valid_state(state):
        abort(403)

    code = request.args.get("code")
    token = get_token(code)

    with open("src/credentials/trakt_token.json", "w") as file:
        json.dump(token, file, indent=2)

    # Flask can't directly return a dict reliably; return JSON text
    return app.response_class(
        response=json.dumps(token, indent=2),
        status=200,
        mimetype="application/json",
    )


def make_authorization_url() -> str:
    state = str(uuid4())
    save_created_state(state)

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "state": state,
        "redirect_uri": REDIRECT_URI,
        "duration": "temporary",
    }
    return "https://trakt.tv/oauth/authorize?" + urlencode(params)


def save_created_state(state: str) -> None:
    global STATE
    STATE = state


def is_valid_state(state: str) -> bool:
    return STATE == state


def get_token(code: str) -> dict:
    post_data = {
        "client_id": CLIENT_ID,
        "client_secret": SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    r = requests.post(
        "https://api.trakt.tv/oauth/token",
        json=post_data,
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    app.run(port=3000)
