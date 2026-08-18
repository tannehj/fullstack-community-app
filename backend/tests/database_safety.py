import os

from psycopg2.extensions import parse_dsn


def normalized_host(host):
    host = host.lower()

    if host in {"localhost", "127.0.0.1", "::1"}:
        return "localhost"

    return host


def database_identity(database_url):
    try:
        connection = parse_dsn(database_url)
    except Exception as error:
        raise RuntimeError("TEST_DATABASE_URL must be a valid PostgreSQL URL") from error

    return (
        normalized_host(connection.get("host", "")),
        connection.get("port", "5432"),
        connection.get("dbname", ""),
    )


def validate_test_database_url(test_database_url, database_url):
    if not test_database_url:
        raise RuntimeError(
            "TEST_DATABASE_URL is required; refusing to run database tests"
        )

    if database_url and (
        test_database_url == database_url
        or database_identity(test_database_url) == database_identity(database_url)
    ):
        raise RuntimeError(
            "TEST_DATABASE_URL must not point to the DATABASE_URL database"
        )

    return test_database_url


def require_test_database_url():
    return validate_test_database_url(
        os.getenv("TEST_DATABASE_URL"),
        os.getenv("DATABASE_URL"),
    )
