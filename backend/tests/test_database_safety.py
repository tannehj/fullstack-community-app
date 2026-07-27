import pytest

from database_safety import validate_test_database_url


def test_test_database_url_is_required():
    with pytest.raises(RuntimeError, match="TEST_DATABASE_URL is required"):
        validate_test_database_url(None, None)


def test_test_database_url_must_not_match_database_url():
    database_url = "postgresql://user:password@localhost:5432/community_app"

    with pytest.raises(RuntimeError, match="must not point"):
        validate_test_database_url(database_url, database_url)


def test_equivalent_database_urls_are_rejected():
    test_database_url = (
        "postgresql://test_user:test_password@localhost:5432/community_app_test"
    )
    database_url = (
        "postgresql://app_user:app_password@localhost:5432/community_app_test"
    )

    with pytest.raises(RuntimeError, match="must not point"):
        validate_test_database_url(test_database_url, database_url)


def test_equivalent_local_hosts_are_rejected():
    test_database_url = (
        "postgresql://test_user:test_password@127.0.0.1:5432/community_app_test"
    )
    database_url = (
        "postgresql://app_user:app_password@localhost:5432/community_app_test"
    )

    with pytest.raises(RuntimeError, match="must not point"):
        validate_test_database_url(test_database_url, database_url)


def test_separate_test_database_is_accepted():
    test_database_url = (
        "postgresql://user:password@localhost:5432/community_app_test"
    )
    database_url = "postgresql://user:password@localhost:5432/community_app"

    assert (
        validate_test_database_url(test_database_url, database_url)
        == test_database_url
    )
