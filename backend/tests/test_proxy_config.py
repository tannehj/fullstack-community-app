import os
from pathlib import Path
import subprocess
import sys


BACKEND_DIRECTORY = Path(__file__).resolve().parents[1]


def import_app(app_env, trusted_proxy_count=None):
    environment = os.environ.copy()
    environment["SECRET_KEY"] = "proxy-config-test-secret"
    environment["APP_ENV"] = app_env

    if trusted_proxy_count is None:
        environment.pop("TRUSTED_PROXY_COUNT", None)
    else:
        environment["TRUSTED_PROXY_COUNT"] = trusted_proxy_count

    return subprocess.run(
        [
            sys.executable,
            "-c",
            "import app; print(type(app.app.wsgi_app).__name__)",
        ],
        cwd=BACKEND_DIRECTORY,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def test_local_startup_defaults_to_no_trusted_proxy():
    result = import_app("development")

    assert result.returncode == 0
    assert result.stdout.strip() == "method"


def test_production_requires_trusted_proxy_count():
    result = import_app("production")

    assert result.returncode != 0
    assert (
        "TRUSTED_PROXY_COUNT environment variable is required in production"
        in result.stderr
    )


def test_production_rejects_zero_trusted_proxies():
    result = import_app("production", "0")

    assert result.returncode != 0
    assert "TRUSTED_PROXY_COUNT must be at least 1 in production" in result.stderr


def test_production_wraps_app_with_configured_proxy_count():
    result = import_app("production", "1")

    assert result.returncode == 0
    assert result.stdout.strip() == "ProxyFix"
