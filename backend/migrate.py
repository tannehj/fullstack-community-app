from pathlib import Path

from app import get_db_connection


MIGRATIONS_DIRECTORY = Path(__file__).parent / "migrations"


def run_migrations():
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename TEXT PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

        migration_files = sorted(MIGRATIONS_DIRECTORY.glob("*.sql"))

        for migration_file in migration_files:
            cursor.execute(
                "SELECT 1 FROM schema_migrations WHERE filename = %s",
                (migration_file.name,)
            )

            if cursor.fetchone():
                print(f"Already applied: {migration_file.name}")
                continue

            print(f"Applying: {migration_file.name}")

            migration_sql = migration_file.read_text()
            cursor.execute(migration_sql)

            cursor.execute(
                "INSERT INTO schema_migrations (filename) VALUES (%s)",
                (migration_file.name,)
            )

            conn.commit()
            print(f"Applied: {migration_file.name}")

        cursor.close()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    run_migrations()