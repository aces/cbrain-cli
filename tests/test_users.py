import json
import urllib.error
from unittest.mock import MagicMock

from cbrain_cli.users import user_details, whoami_user
from tests.conftest import URL, make_args, parse_json_output, patch_module_locals


def test_user_details_http_error_returns_none(monkeypatch, capsys):
    patch_module_locals(monkeypatch, "cbrain_cli.users")
    monkeypatch.setattr(
        "urllib.request.urlopen",
        MagicMock(side_effect=urllib.error.HTTPError(URL, 500, "Err", {}, None)),
    )
    assert user_details(1) is None
    assert "Server error (500)" in capsys.readouterr().out


def test_user_details_unexpected_error_returns_none(monkeypatch, capsys):
    patch_module_locals(monkeypatch, "cbrain_cli.users")

    def boom(_req):
        raise ValueError("parse fail")

    monkeypatch.setattr("urllib.request.urlopen", boom)
    assert user_details(1) is None
    assert "Error getting user details" in capsys.readouterr().out


def test_whoami_missing_credentials_json(capsys, monkeypatch):
    monkeypatch.setattr("cbrain_cli.users.user_id", None)
    monkeypatch.setattr("cbrain_cli.users.cbrain_url", None)
    monkeypatch.setattr("cbrain_cli.users.api_token", None)
    assert whoami_user(make_args(json=True)) == 1
    assert parse_json_output(capsys)["logged_in"] is False


def test_whoami_missing_credentials_plain(capsys, monkeypatch):
    monkeypatch.setattr("cbrain_cli.users.user_id", None)
    monkeypatch.setattr("cbrain_cli.users.cbrain_url", None)
    monkeypatch.setattr("cbrain_cli.users.api_token", None)
    assert whoami_user(make_args()) == 1
    assert "Credential file is missing" in capsys.readouterr().out


def test_whoami_json_output(monkeypatch, capsys):
    patch_module_locals(monkeypatch, "cbrain_cli.users", user_id=1)
    monkeypatch.setattr(
        "cbrain_cli.users.user_details",
        lambda _: {"login": "admin", "full_name": "Admin User"},
    )
    assert whoami_user(make_args(json=True)) == 0
    result = parse_json_output(capsys)
    assert result["login"] == "admin"
    assert result["server"] == URL


def test_whoami_plain_output(monkeypatch, capsys):
    patch_module_locals(monkeypatch, "cbrain_cli.users", user_id=1)
    monkeypatch.setattr(
        "cbrain_cli.users.user_details",
        lambda _: {"login": "admin", "full_name": "Admin User"},
    )
    assert whoami_user(make_args()) is None
    assert "Current user: admin" in capsys.readouterr().out


def test_whoami_version_token_mismatch_warning(monkeypatch, capsys):
    patch_module_locals(monkeypatch, "cbrain_cli.users", user_id=1)
    monkeypatch.setattr(
        "cbrain_cli.users.user_details",
        lambda _: {"login": "admin", "full_name": "Admin User"},
    )
    mock_http_response = MagicMock()
    mock_http_response.__enter__.return_value.read.return_value = json.dumps(
        {"user_id": 99, "cbrain_api_token": "other-token"}
    ).encode()
    mock_http_response.__exit__.return_value = False
    monkeypatch.setattr("urllib.request.urlopen", MagicMock(return_value=mock_http_response))
    assert whoami_user(make_args(version=True)) is None
    out = capsys.readouterr().out
    assert "WARNING: User ID mismatch" in out
    assert "Token mismatch" in out
