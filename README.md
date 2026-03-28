# Calendar

A personal activity and media tracking system that pulls data from multiple sources and writes everything into Google Calendar.

## What it does

- **Activity tracking** — converts exports from [Timing](https://timingapp.com/) into calendar events, with icons, locations, and sub-activity breakdowns
- **Media tracking** — syncs movie and TV watch history from [Trakt.tv](https://trakt.tv/) into calendar events with accurate durations
- **Location tracking** — matches GPS coordinates from [OwnTracks](https://owntracks.org/) to known locations and updates calendar event times accordingly
- **Child activity tracking** — imports baby/child tracking CSVs (feeds, naps, etc.) into calendar events

## Prerequisites

- Python 3.12
- [Pipenv](https://pipenv.pypa.io/)
- A PostgreSQL instance running OwnTracks (for location tracking)

## Setup

### 1. Install dependencies

```bash
pipenv install
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set `TRAKT_CLIENT_ID` (and optionally `PIPENV_PYTHON`).

### 3. Add credentials

Create the following files in `src/credentials/` (all gitignored):

| File | Contents |
|------|----------|
| `credentials.json` | Google OAuth client secret (download from [Google Cloud Console](https://console.cloud.google.com/)) |
| `trakt_token.json` | Trakt OAuth token — run `pipenv run python get_token.py` to generate |
| `own_tracks.json` | PostgreSQL connection: `{"host": "...", "database": "...", "user": "...", "password": "..."}` |

`token.pickle` (Google auth token) is created automatically on first run.

### 4. Set up data files

```
data/
├── geo_locations.csv      # Your locations — use script 8 to add new ones
├── activity/
│   ├── user/              # Drop Timing exports here as "All Activities.csv"
│   └── partner/
└── child/                 # Drop child tracking CSVs here
```

On first run, `data/calendars.json` is auto-generated from your Google Calendar list.

## Usage

```bash
pipenv run python run.py
```

Running without arguments shows an interactive menu. To run specific tasks:

```bash
pipenv run python run.py --task "Update calendar"
pipenv run python run.py --n 0,1        # run tasks 0 and 1
pipenv run python run.py --n 0-3        # run tasks 0 through 3
```

### Scripts

| # | Name | Description |
|---|------|-------------|
| 0 | Parse timing export | Processes a Timing.app CSV export into per-day JSON/CSV files |
| 1 | Update calendar | Pushes processed activity JSON to Google Calendar for a date range |
| 2 | Parse Child export | Imports child tracking CSVs (feeds, naps, etc.) into calendar |
| 3 | Partner default working day | Fills in a default 9–12 / 13–18 work schedule for the partner calendar |
| 4 | Add Trakt watches to calendar | Syncs movie and TV watch history from Trakt into calendar |
| 5 | Add episodes to history | Backfills a TV series into Trakt history and calendar |
| 6 | Add movie to history | Adds a single movie to Trakt history and calendar |
| 7 | Update event times | Refines event start/end times using OwnTracks GPS data |
| 8 | Add new location | Interactive prompt to add a location to `geo_locations.csv` |
| 9 | Print locations | Displays all known locations in a table |

## Project structure

```
src/
├── connectors/        # Google Calendar, Trakt, OwnTracks API clients
├── data/              # Singletons for calendars, locations, icons
├── models/            # Pydantic models (activities, events, locations, Trakt)
├── scripts/           # Runnable scripts (activity, media, location)
├── utils/             # Formatting, file I/O, logging, prompts
└── address_parser.py  # Parses addresses into country-specific models
```

## Development

```bash
pipenv install --dev
pipenv run pytest
```

Pre-commit hooks (mypy, flake8, ruff) are configured in `.pre-commit-config.yaml`.
