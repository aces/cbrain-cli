import argparse

import pytest

from cbrain_cli.cli_utils import CliApiError, CliValidationError
from cbrain_cli.sessions import create_session, logout_session


def test_create_session_already_logged_in(sessions_creds_file, capsys):
    import json

    sessions_creds_file.write_text(
        json.dumps({"api_token": "tok", "cbrain_url": "http://localhost:3000"})
    )
    result = create_session(argparse.Namespace())
    assert result == 1
    assert "Already logged in" in capsys.readouterr().out


def test_create_session_empty_credentials_file_allows_login(
    sessions_creds_file, monkeypatch, capsys
):
    """Empty/corrupt credentials file should not block re-login."""
    sessions_creds_file.write_text("{}")
    inputs = iter(["http://localhost:3000", "admin"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("getpass.getpass", lambda _: "secret")
    monkeypatch.setattr(
        "cbrain_cli.cli_utils.CbrainClient.post_form",
        lambda self, *_a, **_k: {"cbrain_api_token": "newtok", "user_id": 1},
    )
    result = create_session(argparse.Namespace())
    assert result == 0


def test_create_session_empty_username_raises(monkeypatch, sessions_creds_file):
    inputs = iter(["http://localhost:3000", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    with pytest.raises(CliValidationError, match="[Uu]sername"):
        create_session(argparse.Namespace())


def test_create_session_empty_password_raises(monkeypatch, sessions_creds_file):
    inputs = iter(["http://localhost:3000", "admin"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("getpass.getpass", lambda _: "")
    with pytest.raises(CliValidationError, match="[Pp]assword"):
        create_session(argparse.Namespace())


def test_create_session_no_token_in_response_returns_1(monkeypatch, sessions_creds_file, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "admin")
    monkeypatch.setattr("getpass.getpass", lambda _: "secret")
    monkeypatch.setattr(
        "cbrain_cli.cli_utils.CbrainClient.post_form", lambda self, *_: {"user_id": 1}
    )
    result = create_session(argparse.Namespace())
    assert result == 1
    assert "Login failed" in capsys.readouterr().out


def test_create_session_success_saves_credentials(monkeypatch, sessions_creds_file):
    monkeypatch.setattr("builtins.input", lambda _: "admin")
    monkeypatch.setattr("getpass.getpass", lambda _: "secret")
    monkeypatch.setattr(
        "cbrain_cli.cli_utils.CbrainClient.post_form",
        lambda self, *_: {"cbrain_api_token": "tok123", "user_id": 99},
    )
    result = create_session(argparse.Namespace())
    assert result == 0
    assert sessions_creds_file.exists()


def test_logout_session_not_logged_in(sessions_creds_file, capsys):
    result = logout_session(argparse.Namespace())
    assert result == 0
    assert "Not logged in" in capsys.readouterr().out


def test_logout_session_corrupt_file_removes_it(sessions_creds_file, capsys):
    sessions_creds_file.write_text("not valid json")
    result = logout_session(argparse.Namespace())
    assert result == 0
    assert not sessions_creds_file.exists()


def test_logout_session_no_api_token_removes_file_without_http(sessions_creds_file, capsys):
    """Incomplete credentials file is removed with no HTTP call."""
    sessions_creds_file.write_text('{"cbrain_url": "http://localhost:3000"}')
    result = logout_session(argparse.Namespace())
    assert result == 0
    assert not sessions_creds_file.exists()


def test_logout_session_success_sends_delete_and_removes_file(
    monkeypatch, sessions_creds_file, capsys
):
    sessions_creds_file.write_text('{"api_token": "tok", "cbrain_url": "http://localhost:3000"}')
    monkeypatch.setattr("cbrain_cli.cli_utils.CbrainClient.send", lambda self, *_, **__: ({}, 200))
    result = logout_session(argparse.Namespace())
    assert result == 0
    assert not sessions_creds_file.exists()
    assert "Successfully logged out" in capsys.readouterr().out


def test_logout_session_server_401_still_removes_file(monkeypatch, sessions_creds_file, capsys):
    sessions_creds_file.write_text('{"api_token": "tok", "cbrain_url": "http://localhost:3000"}')

    def _raise_401(self, *_, **__):
        raise CliApiError("Unauthorized", status=401)

    monkeypatch.setattr("cbrain_cli.cli_utils.CbrainClient.send", _raise_401)
    result = logout_session(argparse.Namespace())
    assert result == 0
    assert not sessions_creds_file.exists()
    assert "Session already expired" in capsys.readouterr().out


def test_create_session_uses_default_url(monkeypatch, sessions_creds_file):
    inputs = iter(["", "admin"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("getpass.getpass", lambda _: "secret")
    monkeypatch.setattr(
        "cbrain_cli.cli_utils.CbrainClient.post_form",
        lambda self, url, _: {"cbrain_api_token": "tok123", "user_id": 99},
    )
    result = create_session(argparse.Namespace())
    assert result == 0
