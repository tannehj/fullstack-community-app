from concurrent.futures import ThreadPoolExecutor

import psycopg2
import pytest
from werkzeug.middleware.proxy_fix import ProxyFix

import app as app_module
from conftest import TEST_DATABASE_URL


def register(client, csrf_headers, **overrides):
    registration = {
        "name": "Tanneh",
        "username": "tanneh",
        "password": "password",
    }
    registration.update(overrides)
    return client.post("/register", json=registration, headers=csrf_headers)


def login(
    client,
    csrf_headers,
    username="missing",
    password="password",
    remote_addr="127.0.0.1",
    extra_headers=None,
):
    headers = dict(csrf_headers)

    if extra_headers:
        headers.update(extra_headers)

    return client.post(
        "/login",
        json={"username": username, "password": password},
        headers=headers,
        environ_overrides={"REMOTE_ADDR": remote_addr},
    )


@pytest.fixture
def fast_failed_password_check(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "check_password_hash",
        lambda password_hash, password: False,
    )


def get_rate_limit_record(bucket_type, bucket_key):
    conn = psycopg2.connect(TEST_DATABASE_URL)

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT attempt_count
            FROM login_rate_limits
            WHERE bucket_type = %s AND bucket_key = %s
            """,
            (bucket_type, bucket_key),
        )
        return cursor.fetchone()
    finally:
        conn.close()


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


def test_account_login_limit_returns_generic_429(
    client,
    csrf_headers,
    fast_failed_password_check,
):
    for _ in range(10):
        response = login(client, csrf_headers)
        assert response.status_code == 401

    response = login(client, csrf_headers)

    assert response.status_code == 429
    assert response.get_json() == {
        "error": "Too many login attempts. Please try again later."
    }
    assert 1 <= int(response.headers["Retry-After"]) <= 900
    assert response.headers["Cache-Control"] == "no-store"


def test_normalized_username_shares_account_limit(
    client,
    csrf_headers,
    fast_failed_password_check,
):
    for _ in range(5):
        assert login(
            client,
            csrf_headers,
            username=" missing ",
        ).status_code == 401

    for _ in range(5):
        assert login(
            client,
            csrf_headers,
            username="missing",
        ).status_code == 401

    assert login(
        client,
        csrf_headers,
        username="missing",
    ).status_code == 429


def test_client_ip_login_limit_spans_usernames(
    client,
    csrf_headers,
    fast_failed_password_check,
):
    for attempt in range(30):
        response = login(
            client,
            csrf_headers,
            username=f"missing-{attempt}",
            remote_addr="198.51.100.10",
        )
        assert response.status_code == 401

    response = login(
        client,
        csrf_headers,
        username="missing-30",
        remote_addr="198.51.100.10",
    )
    assert response.status_code == 429


def test_retry_after_uses_only_the_exceeded_limit(
    client,
    csrf_headers,
    fast_failed_password_check,
):
    for attempt in range(30):
        assert login(
            client,
            csrf_headers,
            username=f"missing-{attempt}",
            remote_addr="198.51.100.11",
        ).status_code == 401

    ip_key = app_module.get_login_rate_limit_key(
        "ip",
        "198.51.100.11",
    )
    conn = psycopg2.connect(TEST_DATABASE_URL)

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE login_rate_limits
            SET expires_at = CURRENT_TIMESTAMP + INTERVAL '30 seconds'
            WHERE bucket_type = 'ip' AND bucket_key = %s
            """,
            (ip_key,),
        )
        conn.commit()
    finally:
        conn.close()

    response = login(
        client,
        csrf_headers,
        username="new-account",
        remote_addr="198.51.100.11",
    )

    assert response.status_code == 429
    assert 1 <= int(response.headers["Retry-After"]) <= 30


def test_successful_login_clears_account_limit(
    client,
    csrf_headers,
    monkeypatch,
):
    assert register(client, csrf_headers).status_code == 201
    monkeypatch.setattr(
        app_module,
        "check_password_hash",
        lambda password_hash, password: password == "password",
    )

    for _ in range(9):
        assert login(
            client,
            csrf_headers,
            username="tanneh",
            password="wrong-password",
        ).status_code == 401

    assert login(
        client,
        csrf_headers,
        username="tanneh",
        password="password",
    ).status_code == 200

    account_key = app_module.get_login_rate_limit_key(
        "account",
        "tanneh",
    )
    assert get_rate_limit_record("account", account_key) is None

    assert login(
        client,
        csrf_headers,
        username="tanneh",
        password="wrong-password",
    ).status_code == 401


def test_expired_limits_are_reset_and_cleaned_up(
    client,
    csrf_headers,
    fast_failed_password_check,
):
    for _ in range(10):
        assert login(client, csrf_headers).status_code == 401

    conn = psycopg2.connect(TEST_DATABASE_URL)

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE login_rate_limits
            SET expires_at = CURRENT_TIMESTAMP - INTERVAL '1 second'
            """
        )
        cursor.execute(
            """
            INSERT INTO login_rate_limits (
                bucket_type,
                bucket_key,
                window_started_at,
                expires_at,
                attempt_count
            )
            VALUES (
                'account',
                %s,
                CURRENT_TIMESTAMP - INTERVAL '16 minutes',
                CURRENT_TIMESTAMP - INTERVAL '1 minute',
                1
            )
            """,
            ("0" * 64,),
        )
        conn.commit()
    finally:
        conn.close()

    assert login(client, csrf_headers).status_code == 401

    account_key = app_module.get_login_rate_limit_key(
        "account",
        "missing",
    )
    assert get_rate_limit_record("account", account_key) == (1,)
    assert get_rate_limit_record("account", "0" * 64) is None


def test_nonexistent_user_runs_dummy_password_check(
    client,
    csrf_headers,
    monkeypatch,
):
    checked_hashes = []

    def record_password_hash(password_hash, password):
        checked_hashes.append(password_hash)
        return False

    monkeypatch.setattr(
        app_module,
        "check_password_hash",
        record_password_hash,
    )

    assert login(client, csrf_headers).status_code == 401
    assert checked_hashes == [app_module.DUMMY_PASSWORD_HASH]


def test_rate_limit_updates_are_shared_across_database_connections():
    bucket_key = app_module.get_login_rate_limit_key(
        "account",
        "shared-worker-test",
    )

    def record_attempt():
        conn = psycopg2.connect(TEST_DATABASE_URL)

        try:
            cursor = conn.cursor()
            attempt_count, _ = app_module.record_login_attempt(
                cursor,
                "account",
                bucket_key,
            )
            conn.commit()
            return attempt_count
        finally:
            conn.close()

    with ThreadPoolExecutor(max_workers=5) as executor:
        attempt_counts = list(executor.map(
            lambda unused: record_attempt(),
            range(10),
        ))

    assert sorted(attempt_counts) == list(range(1, 11))
    assert get_rate_limit_record("account", bucket_key) == (10,)


def test_local_mode_ignores_forwarded_client_ip(
    client,
    csrf_headers,
    fast_failed_password_check,
):
    assert login(
        client,
        csrf_headers,
        remote_addr="198.51.100.20",
        extra_headers={"X-Forwarded-For": "203.0.113.20"},
    ).status_code == 401

    direct_ip_key = app_module.get_login_rate_limit_key(
        "ip",
        "198.51.100.20",
    )
    forwarded_ip_key = app_module.get_login_rate_limit_key(
        "ip",
        "203.0.113.20",
    )

    assert get_rate_limit_record("ip", direct_ip_key) == (1,)
    assert get_rate_limit_record("ip", forwarded_ip_key) is None


def test_trusted_proxy_uses_rightmost_forwarded_client_ip(
    client,
    csrf_headers,
    fast_failed_password_check,
):
    original_wsgi_app = app_module.app.wsgi_app
    app_module.app.wsgi_app = ProxyFix(
        original_wsgi_app,
        x_for=1,
        x_proto=1,
    )

    try:
        response = login(
            client,
            csrf_headers,
            remote_addr="10.0.0.5",
            extra_headers={
                "X-Forwarded-For": (
                    "192.0.2.20, 203.0.113.20:4567"
                ),
                "X-Forwarded-Proto": "https",
            },
        )
    finally:
        app_module.app.wsgi_app = original_wsgi_app

    assert response.status_code == 401

    trusted_ip_key = app_module.get_login_rate_limit_key(
        "ip",
        "203.0.113.20",
    )
    spoofed_ip_key = app_module.get_login_rate_limit_key(
        "ip",
        "192.0.2.20",
    )

    assert get_rate_limit_record("ip", trusted_ip_key) == (1,)
    assert get_rate_limit_record("ip", spoofed_ip_key) is None
