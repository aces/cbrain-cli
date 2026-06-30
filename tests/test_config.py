import json
import os

import pytest

from cbrain_cli.config import auth_headers, load_credentials, save_credentials
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
