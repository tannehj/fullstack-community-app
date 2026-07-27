import os
import sys
from pathlib import Path

import psycopg2
import pytest

from database_safety import require_test_database_url


TEST_DATABASE_URL = require_test_database_url()

BACKEND_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIRECTORY))

os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("SECRET_KEY", "pytest-secret-key")
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("TRUSTED_PROXY_COUNT", "0")

import app as app_module
import migrate


def drop_test_schema():
    conn = psycopg2.connect(TEST_DATABASE_URL)

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            DROP TABLE IF EXISTS
                login_rate_limits,
                stories,
                users,
                schema_migrations
            CASCADE
            """
        )
        conn.commit()
        cursor.close()
    finally:
        conn.close()


@pytest.fixture(scope="session", autouse=True)
def database_schema():
    drop_test_schema()
    migrate.run_migrations()

    yield

    drop_test_schema()


@pytest.fixture(autouse=True)
def clean_database(database_schema):
    conn = psycopg2.connect(TEST_DATABASE_URL)

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            TRUNCATE login_rate_limits, stories, users
            RESTART IDENTITY CASCADE
            """
        )
        conn.commit()
        cursor.close()
    finally:
        conn.close()


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


@pytest.fixture
def csrf_headers(client):
    response = client.get("/csrf-token")
    assert response.status_code == 200
    return {"X-CSRF-Token": response.get_json()["csrf_token"]}
