import json
import os

import pytest

from cbrain_cli.config import (
    ACTIVE_SESSION_KEY,
    auth_headers,
    cli_session_not_found,
    load_credentials,
    resolve_session_credentials,
    save_credentials,
    update_active_credentials,
)
from tests.conftest import CREDS_FILE, patch_credentials_file, sample_credentials


def test_auth_headers_contains_bearer_token():
    headers = auth_headers("mytoken")
    assert headers["Authorization"] == "Bearer mytoken"
    assert headers["Accept"] == "application/json"


def test_load_credentials_missing_file(creds_file):
    assert load_credentials() is None


def test_load_credentials_corrupt_json(creds_file):
    creds_file.write_text("not valid json")
    assert load_credentials() is None


def test_save_and_load_credentials_round_trip(creds_file):
    data = sample_credentials()
    save_credentials(data)
    assert load_credentials() == data


def test_save_credentials_creates_parent_directory(tmp_path, monkeypatch):
    nested = tmp_path / "deep" / "nested" / CREDS_FILE
    patch_credentials_file(monkeypatch, nested)
    save_credentials({"key": "value"})
    assert nested.exists()
    assert json.loads(nested.read_text()) == {"key": "value"}


@pytest.mark.skipif(os.name != "posix", reason="POSIX file permissions")
def test_save_credentials_private_mode(creds_file):
    save_credentials({"key": "value"})
    assert (creds_file.stat().st_mode & 0o777) == 0o600


@pytest.mark.skipif(os.name != "posix", reason="POSIX file permissions")
def test_save_credentials_tightens_loose_permissions(creds_file):
    creds_file.write_text("{}")
    os.chmod(creds_file, 0o644)
    save_credentials({"key": "value"})
    assert (creds_file.stat().st_mode & 0o777) == 0o600


@pytest.mark.skipif(os.name != "posix", reason="POSIX file permissions")
def test_save_credentials_preserves_restrictive_permissions(creds_file):
    creds_file.write_text("{}")
    os.chmod(creds_file, 0o600)
    save_credentials({"key": "updated"})
    assert (creds_file.stat().st_mode & 0o777) == 0o600
    assert load_credentials() == {"key": "updated"}


def test_save_credentials_non_posix_branch(monkeypatch, creds_file):
    monkeypatch.setattr("os.name", "nt")
    save_credentials({"key": "value"})
    assert load_credentials() == {"key": "value"}


def test_update_active_credentials_honors_cli_session_override(monkeypatch, creds_file):
    creds_file.write_text(
        json.dumps(
            {
                ACTIVE_SESSION_KEY: "default",
                "default": {"api_token": "a", "cbrain_url": "http://localhost:3000"},
                "prod": {"api_token": "b", "cbrain_url": "http://localhost:3000"},
            }
        )
    )
    monkeypatch.setattr("cbrain_cli.cli_utils.session_name", "prod")
    monkeypatch.setattr("cbrain_cli.cli_utils.session_specified", True)

    update_active_credentials({"current_group_id": 7})

    saved = load_credentials()
    assert saved["prod"]["current_group_id"] == 7
    assert "current_group_id" not in saved["default"]


def test_resolve_session_credentials_honors_cli_session_override(monkeypatch, creds_file):
    data = {
        ACTIVE_SESSION_KEY: "default",
        "default": {"api_token": "a", "user_id": 1},
        "prod": {"api_token": "b", "user_id": 2},
    }
    monkeypatch.setattr("cbrain_cli.cli_utils.session_name", "prod")
    monkeypatch.setattr("cbrain_cli.cli_utils.session_specified", True)

    resolved = resolve_session_credentials(data)
    assert resolved["api_token"] == "b"
    assert resolved["user_id"] == 2


def test_cli_session_not_found(monkeypatch):
    monkeypatch.setattr("cbrain_cli.cli_utils.session_name", "ghost")
    monkeypatch.setattr("cbrain_cli.cli_utils.session_specified", True)
    assert cli_session_not_found() == "ghost"
