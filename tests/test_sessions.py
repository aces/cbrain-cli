import argparse
import urllib.error
from unittest.mock import MagicMock

import pytest

from cbrain_cli.cli_utils import CliValidationError
from cbrain_cli.sessions import create_session, logout_session


def test_create_session_already_logged_in(sessions_creds_file, capsys):
    sessions_creds_file.write_text("{}")
    result = create_session(argparse.Namespace())
    assert result == 1
    assert "Already logged in" in capsys.readouterr().out


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
        "cbrain_cli.sessions.api_post_form", lambda *_: {"user_id": 1}
    )
    result = create_session(argparse.Namespace())
    assert result == 1
    assert "Login failed" in capsys.readouterr().out


def test_create_session_success_saves_credentials(monkeypatch, sessions_creds_file):
    monkeypatch.setattr("builtins.input", lambda _: "admin")
    monkeypatch.setattr("getpass.getpass", lambda _: "secret")
    monkeypatch.setattr(
        "cbrain_cli.sessions.api_post_form",
        lambda *_: {"cbrain_api_token": "tok123", "user_id": 99},
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


def test_logout_session_no_api_token_removes_file_without_http(monkeypatch, sessions_creds_file, capsys):
    """When sessions module-local api_token is None, logout removes file with no HTTP call."""
    sessions_creds_file.write_text('{"api_token": "tok", "cbrain_url": "http://localhost:3000"}')
    # explicitly null out the module-local copies (not reset by _reset_globals)
    monkeypatch.setattr("cbrain_cli.sessions.api_token", None)
    monkeypatch.setattr("cbrain_cli.sessions.cbrain_url", None)
    result = logout_session(argparse.Namespace())
    assert result == 0
    assert not sessions_creds_file.exists()


def test_logout_session_success_sends_delete_and_removes_file(monkeypatch, sessions_creds_file, capsys):
    sessions_creds_file.write_text('{"api_token": "tok", "cbrain_url": "http://localhost:3000"}')
    monkeypatch.setattr("cbrain_cli.sessions.api_token", "tok")
    monkeypatch.setattr("cbrain_cli.sessions.cbrain_url", "http://localhost:3000")
    monkeypatch.setattr("cbrain_cli.sessions.api_send", lambda *_, **__: ({}, 200))
    result = logout_session(argparse.Namespace())
    assert result == 0
    assert not sessions_creds_file.exists()
    assert "Successfully logged out" in capsys.readouterr().out


def test_logout_session_server_401_still_removes_file(monkeypatch, sessions_creds_file, capsys):
    sessions_creds_file.write_text('{"api_token": "tok", "cbrain_url": "http://localhost:3000"}')
    monkeypatch.setattr("cbrain_cli.sessions.api_token", "tok")
    monkeypatch.setattr("cbrain_cli.sessions.cbrain_url", "http://localhost:3000")
    monkeypatch.setattr(
        "cbrain_cli.sessions.api_send",
        MagicMock(
            side_effect=urllib.error.HTTPError(
                "http://localhost:3000/session", 401, "Unauthorized", {}, None
            )
        ),
    )
    result = logout_session(argparse.Namespace())
    assert result == 0
    assert not sessions_creds_file.exists()
    assert "Session already expired" in capsys.readouterr().out


def test_create_session_uses_default_url(monkeypatch, sessions_creds_file):
    inputs = iter(["", "admin"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("getpass.getpass", lambda _: "secret")
    monkeypatch.setattr(
        "cbrain_cli.sessions.api_post_form",
        lambda url, _: {"cbrain_api_token": "tok123", "user_id": 99},
    )
    result = create_session(argparse.Namespace())
    assert result == 0
