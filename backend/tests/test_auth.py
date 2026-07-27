import pytest


def register(client, csrf_headers, **overrides):
    registration = {
        "name": "Tanneh",
        "username": "tanneh",
        "password": "password",
    }
    registration.update(overrides)
    return client.post("/register", json=registration, headers=csrf_headers)


def test_registration_login_current_user_and_logout(client, csrf_headers):
    response = register(client, csrf_headers)
    assert response.status_code == 201

    response = client.post(
        "/login",
        json={"username": "tanneh", "password": "password"},
        headers=csrf_headers,
    )
    assert response.status_code == 200

    response = client.get("/current-user")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Tanneh"

    response = client.post("/logout", headers=csrf_headers)
    assert response.status_code == 200
    assert client.get("/current-user").status_code == 401


def test_duplicate_registration_returns_400(client, csrf_headers):
    assert register(client, csrf_headers).status_code == 201
    assert register(client, csrf_headers).status_code == 400


@pytest.mark.parametrize(
    "request_arguments",
    [
        {},
        {"data": "{", "content_type": "application/json"},
        {"json": []},
        {"json": {"name": "Tanneh", "username": "tanneh"}},
        {
            "json": {
                "name": 1,
                "username": "tanneh",
                "password": "password",
            }
        },
        {
            "json": {
                "name": "n" * 101,
                "username": "tanneh",
                "password": "password",
            }
        },
        {
            "json": {
                "name": "Tanneh",
                "username": "u" * 31,
                "password": "password",
            }
        },
        {
            "json": {
                "name": "Tanneh",
                "username": "tanneh",
                "password": "short",
            }
        },
    ],
)
def test_malformed_registration_returns_400(
    client,
    csrf_headers,
    request_arguments,
):
    response = client.post(
        "/register",
        headers=csrf_headers,
        **request_arguments,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    "request_arguments",
    [
        {},
        {"data": "{", "content_type": "application/json"},
        {"json": []},
        {"json": {"username": "tanneh"}},
        {"json": {"username": 1, "password": "password"}},
    ],
)
def test_malformed_login_returns_400(
    client,
    csrf_headers,
    request_arguments,
):
    response = client.post(
        "/login",
        headers=csrf_headers,
        **request_arguments,
    )
    assert response.status_code == 400


def test_wrong_login_returns_401(client, csrf_headers):
    response = client.post(
        "/login",
        json={"username": "missing", "password": "password"},
        headers=csrf_headers,
    )
    assert response.status_code == 401
