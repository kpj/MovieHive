import pytest
from fastapi.testclient import TestClient

from ..main import app
from ..config import Settings, get_settings


def get_settings_override(path_prefix):
    return lambda: Settings(
        user_database_string="test_user:test_pw",
        jwt_secret_key="123",
        datatbase_directory=path_prefix,
    )


@pytest.fixture
def client(tmp_path):
    app.dependency_overrides[get_settings] = get_settings_override(tmp_path)

    # Context manager is needed to activate lifespans.
    with TestClient(app) as client:
        yield client


class MockIMDB:
    def get_by_name(name: str) -> dict[str, str]:
        return {
            "name": name,
            "actor": [],
            "director": [],
            "creator": [],
            "poster": "",
            "description": "",
            "genre": "",
            "datePublished": "",
        }


@pytest.fixture(autouse=True)
def imdb_path(monkeypatch):
    monkeypatch.setattr("imdbmovies.IMDB", lambda: MockIMDB)


def test_single_round(client):
    # Login.
    response = client.post(
        "/token", data={"username": "test_user", "password": "test_pw"}
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert len(response.json()["access_token"]) > 0

    headers = {"Authorization": f"Bearer {response.json()["access_token"]}"}

    # Add users to game.
    response = client.post("/users", headers=headers, json={"name": "test_user"})
    assert response.status_code == 200
    assert response.json() is None

    # Assert game is empty on startup.
    response = client.get("/rounds", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

    # Submit prompt.
    response = client.post("/round", headers=headers, json={"prompt": "test_prompt"})
    assert response.status_code == 200
    assert response.json() == {
        "player_state": "open",
        "state": "SubmissionState",
    }

    # Check updated round.
    response = client.get("/round", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "prompt": "test_prompt",
        "submissions": [],
    }

    # Submit a movie.
    response = client.post(
        "/submissions",
        headers=headers,
        json={"name": "test_prompt", "comment": "Nice one."},
    )
    assert response.status_code == 200
    assert response.json() == {
        "player_state": "open",
        "state": "VotingState",
    }

    # Check updated round.
    response = client.get("/round", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "prompt": "test_prompt",
        "submissions": [
            {
                "comments": [
                    {
                        "author": {
                            "id": 1,
                            "name": "test_user",
                            "voted_submission_id": None,
                        },
                        "author_id": 1,
                        "submission_id": 1,
                        "text": "Nice one.",
                    },
                ],
                "id": 1,
                "movie": {
                    "actors": "",
                    "description": "",
                    "directors": "",
                    "genre": "",
                    "id": 1,
                    "name": "test_prompt",
                    "poster_url": "",
                    "release_date": "",
                    "requested_name": "test_prompt",
                },
                "movie_id": 1,
                "round_id": 1,
                "submitting_user": {
                    "id": 1,
                    "name": "test_user",
                    "voted_submission_id": None,
                },
                "submitting_user_id": 1,
                "voting_users": [],
            },
        ],
    }

    # Cast a vote.
    response = client.post(
        "/vote",
        headers=headers,
        json={"submission_id": 1, "all_comments": {1: "Another comment."}},
    )
    assert response.status_code == 200
    assert response.json() == {
        "player_state": None,
        "state": "OverviewState",
    }

    # Check updated round.
    response = client.get("/round", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "prompt": "test_prompt",
        "submissions": [
            {
                "comments": [
                    {
                        "author": {
                            "id": 1,
                            "name": "test_user",
                            "voted_submission_id": 1,
                        },
                        "author_id": 1,
                        "submission_id": 1,
                        "text": "Nice one.",
                    },
                    {
                        "author": {
                            "id": 1,
                            "name": "test_user",
                            "voted_submission_id": 1,
                        },
                        "author_id": 1,
                        "submission_id": 1,
                        "text": "Another comment.",
                    },
                ],
                "id": 1,
                "movie": {
                    "actors": "",
                    "description": "",
                    "directors": "",
                    "genre": "",
                    "id": 1,
                    "name": "test_prompt",
                    "poster_url": "",
                    "release_date": "",
                    "requested_name": "test_prompt",
                },
                "movie_id": 1,
                "round_id": 1,
                "submitting_user": {
                    "id": 1,
                    "name": "test_user",
                    "voted_submission_id": 1,
                },
                "submitting_user_id": 1,
                "voting_users": [
                    {
                        "id": 1,
                        "name": "test_user",
                        "voted_submission_id": 1,
                    },
                ],
            },
        ],
    }
