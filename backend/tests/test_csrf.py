import pytest


def test_csrf_token_is_stable_for_session(client):
    first_response = client.get("/csrf-token")
    second_response = client.get("/csrf-token")

    assert first_response.status_code == 200
    assert first_response.headers["Cache-Control"] == "no-store"
    assert (
        first_response.get_json()["csrf_token"]
        == second_response.get_json()["csrf_token"]
    )


@pytest.mark.parametrize(
    ("method", "route", "body"),
    [
        ("post", "/register", {
            "name": "Tanneh",
            "username": "tanneh",
            "password": "password",
        }),
        ("post", "/login", {
            "username": "tanneh",
            "password": "password",
        }),
        ("post", "/logout", None),
        ("post", "/stories", {"story": "Story"}),
        ("patch", "/stories/1", {"story": "Updated story"}),
        ("delete", "/stories/1", None),
    ],
)
def test_state_changes_reject_missing_and_invalid_csrf(
    client,
    method,
    route,
    body,
):
    request_method = getattr(client, method)

    response = request_method(route, json=body)
    assert response.status_code == 403

    response = request_method(
        route,
        json=body,
        headers={"X-CSRF-Token": "invalid-token"},
    )
    assert response.status_code == 403
