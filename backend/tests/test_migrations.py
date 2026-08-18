import psycopg2

from conftest import TEST_DATABASE_URL, drop_test_schema
from migrate import run_migrations


def test_migrations_create_schema_and_are_idempotent():
    drop_test_schema()

    run_migrations()
    run_migrations()

    conn = psycopg2.connect(TEST_DATABASE_URL)

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                to_regclass('public.users'),
                to_regclass('public.stories'),
                to_regclass('public.login_rate_limits'),
                to_regclass('public.schema_migrations')
            """
        )
        tables = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) FROM schema_migrations")
        migration_count = cursor.fetchone()[0]
        cursor.close()
    finally:
        conn.close()

    assert tables == (
        "users",
        "stories",
        "login_rate_limits",
        "schema_migrations",
    )
    assert migration_count == 2
