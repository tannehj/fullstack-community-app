import pytest

from app import app


def register_and_login(client, name, username):
    csrf_token = client.get("/csrf-token").get_json()["csrf_token"]
    headers = {"X-CSRF-Token": csrf_token}

    response = client.post(
        "/register",
        json={
            "name": name,
            "username": username,
            "password": "password",
        },
        headers=headers,
    )
    assert response.status_code == 201

    response = client.post(
        "/login",
        json={"username": username, "password": "password"},
        headers=headers,
    )
    assert response.status_code == 200

    return headers


def test_complete_story_flow(client):
    headers = register_and_login(client, "Owner", "owner")

    response = client.post(
        "/stories",
        json={"story": "Original story"},
        headers=headers,
    )
    assert response.status_code == 201
    story_id = response.get_json()["id"]

    response = client.get("/stories")
    assert response.status_code == 200
    assert response.get_json()[0]["story"] == "Original story"

    response = client.patch(
        f"/stories/{story_id}",
        json={"story": "Updated story"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.get_json()["story"] == "Updated story"

    response = client.delete(f"/stories/{story_id}", headers=headers)
    assert response.status_code == 200
    assert client.get("/stories").get_json() == []


@pytest.mark.parametrize("length", [1, 500])
def test_story_boundary_lengths_are_accepted(client, length):
    headers = register_and_login(client, "Owner", "owner")
    response = client.post(
        "/stories",
        json={"story": "s" * length},
        headers=headers,
    )
    assert response.status_code == 201


@pytest.mark.parametrize("story", ["", "   ", "s" * 501])
def test_invalid_story_lengths_return_400(client, story):
    headers = register_and_login(client, "Owner", "owner")
    response = client.post(
        "/stories",
        json={"story": story},
        headers=headers,
    )
    assert response.status_code == 400


@pytest.mark.parametrize("story", ["", "   ", 1, "s" * 501])
def test_invalid_patch_story_content_returns_400(client, story):
    headers = register_and_login(client, "Owner", "owner")
    response = client.post(
        "/stories",
        json={"story": "Original story"},
        headers=headers,
    )
    story_id = response.get_json()["id"]

    response = client.patch(
        f"/stories/{story_id}",
        json={"story": story},
        headers=headers,
    )
    assert response.status_code == 400


def test_unauthenticated_story_requests_return_401(client, csrf_headers):
    assert client.get("/stories").status_code == 401
    assert client.post(
        "/stories",
        json={"story": "Story"},
        headers=csrf_headers,
    ).status_code == 401
    assert client.patch(
        "/stories/1",
        json={"story": "Story"},
        headers=csrf_headers,
    ).status_code == 401
    assert client.delete("/stories/1", headers=csrf_headers).status_code == 401


def test_non_owner_cannot_update_or_delete_story(client):
    owner_headers = register_and_login(client, "Owner", "owner")
    response = client.post(
        "/stories",
        json={"story": "Owner story"},
        headers=owner_headers,
    )
    story_id = response.get_json()["id"]

    other_client = app.test_client()
    other_headers = register_and_login(other_client, "Other", "other")

    assert other_client.patch(
        f"/stories/{story_id}",
        json={"story": "Changed"},
        headers=other_headers,
    ).status_code == 403
    assert other_client.delete(
        f"/stories/{story_id}",
        headers=other_headers,
    ).status_code == 403


def test_missing_story_returns_404(client):
    headers = register_and_login(client, "Owner", "owner")

    assert client.patch(
        "/stories/999",
        json={"story": "Changed"},
        headers=headers,
    ).status_code == 404
    assert client.delete("/stories/999", headers=headers).status_code == 404
