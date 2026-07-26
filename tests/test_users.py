import json
import urllib.error
from unittest.mock import MagicMock

import pytest

from cbrain_cli.cli_utils import CliApiError
from cbrain_cli.users import user_details, whoami_user
from tests.conftest import URL, install_auth, make_args, parse_json_output


def test_user_details_http_error_raises(monkeypatch):
    install_auth()
    monkeypatch.setattr(
        "urllib.request.urlopen",
        MagicMock(side_effect=urllib.error.HTTPError(URL, 500, "Err", {}, None)),
    )
    with pytest.raises(CliApiError) as exc_info:
        user_details(1)
    assert exc_info.value.status == 500


def test_user_details_unexpected_error_raises(monkeypatch):
    install_auth()

    def boom(_req, timeout=None):
        raise ValueError("parse fail")

    monkeypatch.setattr("urllib.request.urlopen", boom)
    with pytest.raises(ValueError, match="parse fail"):
        user_details(1)


def test_whoami_missing_credentials_json(capsys):
    assert whoami_user(make_args(json=True)) == 1
    assert parse_json_output(capsys)["logged_in"] is False


def test_whoami_missing_credentials_plain(capsys):
    assert whoami_user(make_args()) == 1
    assert "Credential file is missing" in capsys.readouterr().out


def test_whoami_json_output(monkeypatch, capsys):
    install_auth(user_id=1)
    monkeypatch.setattr(
        "cbrain_cli.users.user_details",
        lambda _: {"login": "admin", "full_name": "Admin User"},
    )
    assert whoami_user(make_args(json=True)) == 0
    result = parse_json_output(capsys)
    assert result["login"] == "admin"
    assert result["server"] == URL


def test_whoami_plain_output(monkeypatch, capsys):
    install_auth(user_id=1)
    monkeypatch.setattr(
        "cbrain_cli.users.user_details",
        lambda _: {"login": "admin", "full_name": "Admin User"},
    )
    assert whoami_user(make_args()) is None
    assert "Current user: admin" in capsys.readouterr().out


def test_whoami_version_token_mismatch_warning(monkeypatch, capsys):
    install_auth(user_id=1)
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


def test_login_then_whoami_uses_fresh_credentials(monkeypatch, sessions_creds_file, capsys):
    """Verify login/logout/whoami see current credential state in one process."""
    import argparse

    from cbrain_cli.cli_utils import CbrainClient, is_authenticated
    from cbrain_cli.sessions import create_session, logout_session

    client = CbrainClient.from_credentials()
    assert (client.base_url, client.token, client.user_id) == ("", "", None)
    assert is_authenticated() is False
    capsys.readouterr()

    inputs = iter(["", "admin"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("getpass.getpass", lambda _: "secret")
    monkeypatch.setattr(
        "cbrain_cli.cli_utils.CbrainClient.post_form",
        lambda self, *_: {"cbrain_api_token": "fresh-tok", "user_id": 7},
    )
    assert create_session(argparse.Namespace()) == 0
    client = CbrainClient.from_credentials()
    assert (client.base_url, client.token, client.user_id) == (URL, "fresh-tok", 7)
    assert is_authenticated() is True
    capsys.readouterr()

    monkeypatch.setattr(
        "cbrain_cli.users.user_details",
        lambda uid: {"login": "admin", "full_name": "Admin"},
    )
    assert whoami_user(make_args(json=True)) == 0
    assert parse_json_output(capsys)["login"] == "admin"

    monkeypatch.setattr("cbrain_cli.cli_utils.CbrainClient.send", lambda self, *_, **__: ({}, 200))
    assert logout_session(argparse.Namespace()) == 0
    client = CbrainClient.from_credentials()
    assert (client.base_url, client.token, client.user_id) == ("", "", None)
    assert is_authenticated() is False
