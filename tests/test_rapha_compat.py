"""Compatibility boundaries that keep Rapha thin over upstream."""

from pathlib import Path
from types import SimpleNamespace

from core.rapha_env import apply_rapha_env_aliases, is_supported_api_token
from core.middleware import (
    INTERNAL_TOOL_HEADER,
    INTERNAL_TOOL_TOKEN,
    LEGACY_INTERNAL_TOOL_HEADER,
    require_admin,
)
from routes.auth_routes import get_session_cookie


def test_rapha_environment_overrides_upstream_alias():
    environment = {
        "RAPHA_DATA_DIR": "/tmp/rapha-data",
        "ODYSSEUS_DATA_DIR": "/tmp/old-data",
        "RAPHA_INPROCESS_TASKS": "0",
    }
    applied = apply_rapha_env_aliases(environment)
    assert environment["ODYSSEUS_DATA_DIR"] == "/tmp/rapha-data"
    assert environment["ODYSSEUS_INPROCESS_TASKS"] == "0"
    assert applied == {
        "ODYSSEUS_DATA_DIR": "RAPHA_DATA_DIR",
        "ODYSSEUS_INPROCESS_TASKS": "RAPHA_INPROCESS_TASKS",
    }


def test_empty_rapha_environment_does_not_replace_upstream():
    environment = {"RAPHA_DATA_DIR": "", "ODYSSEUS_DATA_DIR": "/tmp/upstream"}
    assert apply_rapha_env_aliases(environment) == {}
    assert environment["ODYSSEUS_DATA_DIR"] == "/tmp/upstream"


def test_current_and_legacy_api_token_prefixes_are_supported():
    assert is_supported_api_token("rph_current") is True
    assert is_supported_api_token("ody_legacy") is True
    assert is_supported_api_token("sk_unknown") is False
    assert is_supported_api_token("") is False


def test_session_cookie_prefers_rapha_and_accepts_legacy():
    current = SimpleNamespace(cookies={"rapha_session": "new", "odysseus_session": "old"})
    legacy = SimpleNamespace(cookies={"odysseus_session": "old"})
    assert get_session_cookie(current) == "new"
    assert get_session_cookie(legacy) == "old"


def test_current_and_legacy_internal_headers_are_accepted():
    app = SimpleNamespace(state=SimpleNamespace(auth_manager=None))
    for header in (INTERNAL_TOOL_HEADER, LEGACY_INTERNAL_TOOL_HEADER):
        request = SimpleNamespace(
            headers={header: INTERNAL_TOOL_TOKEN},
            state=SimpleNamespace(current_user=None),
            app=app,
        )
        assert require_admin(request) is None


def test_local_storage_migration_is_copy_only():
    source = Path(__file__).resolve().parents[1] / "static" / "js" / "storage.js"
    contents = source.read_text(encoding="utf-8")
    assert "localStorage.setItem(target, localStorage.getItem(source))" in contents
    assert "localStorage.removeItem(source)" not in contents
