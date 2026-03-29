from src.models.trakt import Movie, TraktIds


def test_trakt_ids_minimal() -> None:
    ids = TraktIds.model_validate({"trakt": 12345})
    assert ids.trakt == 12345
    assert ids.slug is None
    assert ids.imdb is None


def test_trakt_ids_full() -> None:
    ids = TraktIds.model_validate(
        {
            "trakt": 1,
            "slug": "breaking-bad",
            "imdb": "tt0903747",
            "tmdb": 1396,
            "tvdb": 81189,
        },
    )
    assert ids.slug == "breaking-bad"
    assert ids.imdb == "tt0903747"
    assert ids.tmdb == 1396
    assert ids.tvdb == 81189


def test_movie_with_nested_ids() -> None:
    movie = Movie.model_validate(
        {
            "title": "Test Film",
            "year": 2020,
            "ids": {"trakt": 999, "slug": "test-film-2020"},
        },
    )
    assert movie.title == "Test Film"
    assert movie.year == 2020
    assert movie.ids.trakt == 999
    assert movie.ids.slug == "test-film-2020"
