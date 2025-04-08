import pytest
from fastapi.testclient import TestClient

from ..main import app
from ..config import Settings, get_settings


def get_settings_override(path_prefix):
    return lambda: Settings(
        user_database_string="test_user:test_pw test_user2:test_pw2",
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
    headers_user1 = {"Authorization": f"Bearer {response.json()["access_token"]}"}

    response = client.post(
        "/token", data={"username": "test_user2", "password": "test_pw2"}
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert len(response.json()["access_token"]) > 0
    headers_user2 = {"Authorization": f"Bearer {response.json()["access_token"]}"}

    # Add users to game.
    response = client.post("/users", headers=headers_user1, json={"name": "test_user"})
    assert response.status_code == 200
    assert response.json() is None

    response = client.post("/users", headers=headers_user2, json={"name": "test_user2"})
    assert response.status_code == 200
    assert response.json() is None

    # Assert game is empty on startup.
    response = client.get("/rounds", headers=headers_user1)
    assert response.status_code == 200
    assert response.json() == []

    # Check game is ready for new round.
    response = client.get("/state", headers=headers_user1)
    assert response.status_code == 200
    assert response.json() == {
        "player_state": None,
        "state": "OverviewState",
    }

    # Submit prompt.
    response = client.post(
        "/round", headers=headers_user1, json={"prompt": "test_prompt"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "player_state": "open",
        "state": "SubmissionState",
    }

    # Check updated round.
    response = client.get("/round", headers=headers_user1)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "prompt": "test_prompt",
        "submissions": [],
    }

    response = client.get("/round", headers=headers_user2)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "prompt": "test_prompt",
        "submissions": [],
    }

    # Submit a movie.
    response = client.post(
        "/submissions",
        headers=headers_user1,
        json={"name": "Movie1", "comment": "Comment 1"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "player_state": "closed",
        "state": "SubmissionState",
    }

    response = client.post(
        "/submissions",
        headers=headers_user2,
        json={"name": "Movie2", "comment": "Comment 2"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "player_state": "open",
        "state": "VotingState",
    }

    # Check updated round.
    response = client.get("/round", headers=headers_user1)
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
                        "text": "Comment 1",
                    },
                ],
                "id": 1,
                "movie": {
                    "actors": "",
                    "description": "",
                    "directors": "",
                    "genre": "",
                    "id": 1,
                    "name": "Movie1",
                    "poster_url": "",
                    "release_date": "",
                    "requested_name": "Movie1",
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
            {
                "comments": [
                    {
                        "author": {
                            "id": 2,
                            "name": "test_user2",
                            "voted_submission_id": None,
                        },
                        "author_id": 2,
                        "submission_id": 2,
                        "text": "Comment 2",
                    },
                ],
                "id": 2,
                "movie": {
                    "actors": "",
                    "description": "",
                    "directors": "",
                    "genre": "",
                    "id": 2,
                    "name": "Movie2",
                    "poster_url": "",
                    "release_date": "",
                    "requested_name": "Movie2",
                },
                "movie_id": 2,
                "round_id": 1,
                "submitting_user": {
                    "id": 2,
                    "name": "test_user2",
                    "voted_submission_id": None,
                },
                "submitting_user_id": 2,
                "voting_users": [],
            },
        ],
    }

    # Cast a vote.
    response = client.post(
        "/vote",
        headers=headers_user1,
        json={"submission_id": 1, "all_comments": {1: "Another comment."}},
    )
    assert response.status_code == 200
    assert response.json() == {
        "player_state": "closed",
        "state": "VotingState",
    }

    response = client.post(
        "/vote",
        headers=headers_user2,
        json={
            "submission_id": 1,
            "all_comments": {1: "Final comment.", 2: "And also one here."},
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "player_state": None,
        "state": "OverviewState",
    }

    # Check updated round.
    response = client.get("/round", headers=headers_user1)
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
                        "text": "Comment 1",
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
                    {
                        "author": {
                            "id": 2,
                            "name": "test_user2",
                            "voted_submission_id": 1,
                        },
                        "author_id": 2,
                        "submission_id": 1,
                        "text": "Final comment.",
                    },
                ],
                "id": 1,
                "movie": {
                    "actors": "",
                    "description": "",
                    "directors": "",
                    "genre": "",
                    "id": 1,
                    "name": "Movie1",
                    "poster_url": "",
                    "release_date": "",
                    "requested_name": "Movie1",
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
                    {
                        "id": 2,
                        "name": "test_user2",
                        "voted_submission_id": 1,
                    },
                ],
            },
            {
                "comments": [
                    {
                        "author": {
                            "id": 2,
                            "name": "test_user2",
                            "voted_submission_id": 1,
                        },
                        "author_id": 2,
                        "submission_id": 2,
                        "text": "Comment 2",
                    },
                    {
                        "author": {
                            "id": 2,
                            "name": "test_user2",
                            "voted_submission_id": 1,
                        },
                        "author_id": 2,
                        "submission_id": 2,
                        "text": "And also one here.",
                    },
                ],
                "id": 2,
                "movie": {
                    "actors": "",
                    "description": "",
                    "directors": "",
                    "genre": "",
                    "id": 2,
                    "name": "Movie2",
                    "poster_url": "",
                    "release_date": "",
                    "requested_name": "Movie2",
                },
                "movie_id": 2,
                "round_id": 1,
                "submitting_user": {
                    "id": 2,
                    "name": "test_user2",
                    "voted_submission_id": 1,
                },
                "submitting_user_id": 2,
                "voting_users": [],
            },
        ],
    }

    # Check that new round has started.
    response = client.get("/state", headers=headers_user1)
    assert response.status_code == 200
    assert response.json() == {
        "player_state": None,
        "state": "OverviewState",
    }
