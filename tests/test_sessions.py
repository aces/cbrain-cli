import argparse
import urllib.error

import pytest

from cbrain_cli.cli_utils import CliApiError, CliValidationError
from cbrain_cli.sessions import create_session, list_sessions, logout_session, switch_session


def test_create_session_already_logged_in(sessions_creds_file, monkeypatch, capsys):
    import json

    sessions_creds_file.write_text(
        json.dumps({"api_token": "tok", "cbrain_url": "http://localhost:3000", "user_id": 1})
    )
    monkeypatch.setattr(
        "cbrain_cli.cli_utils.CbrainClient.get",
        lambda self, *_: {"user_id": 1, "cbrain_api_token": "tok"},
    )
    result = create_session(argparse.Namespace())
    assert result == 1
    assert "Already logged in" in capsys.readouterr().out


def test_create_session_expired_token_allows_relogin(sessions_creds_file, monkeypatch, capsys):
    import json

    sessions_creds_file.write_text(
        json.dumps({"api_token": "dead", "cbrain_url": "http://localhost:3000", "user_id": 1})
    )

    def _raise_401(self, *_):
        raise CliApiError("Unauthorized", status=401)

    monkeypatch.setattr("cbrain_cli.cli_utils.CbrainClient.get", _raise_401)
    inputs = iter(["http://localhost:3000", "admin"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("getpass.getpass", lambda _: "secret")
    monkeypatch.setattr(
        "cbrain_cli.cli_utils.CbrainClient.post_form",
        lambda self, *_a, **_k: {"cbrain_api_token": "newtok", "user_id": 1},
    )
    result = create_session(argparse.Namespace())
    assert result == 0
    assert "Saved session expired" in capsys.readouterr().out


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


def test_create_session_unreachable_server_reports_connectivity(
    sessions_creds_file, monkeypatch, capsys
):
    import json

    sessions_creds_file.write_text(
        json.dumps({"api_token": "tok", "cbrain_url": "http://localhost:3000", "user_id": 1})
    )
    monkeypatch.setattr(
        "cbrain_cli.cli_utils.CbrainClient.get",
        lambda self, *_: (_ for _ in ()).throw(urllib.error.URLError("Connection refused")),
    )
    result = create_session(argparse.Namespace())
    assert result == 1
    out = capsys.readouterr().out
    assert "Cannot reach" in out
    assert "Already logged in" not in out


def test_create_session_server_error_reports_status(sessions_creds_file, monkeypatch, capsys):
    import json

    sessions_creds_file.write_text(
        json.dumps({"api_token": "tok", "cbrain_url": "http://localhost:3000", "user_id": 1})
    )
    monkeypatch.setattr(
        "cbrain_cli.cli_utils.CbrainClient.get",
        lambda self, *_: (_ for _ in ()).throw(CliApiError("Server Error", status=500)),
    )
    result = create_session(argparse.Namespace())
    assert result == 1
    out = capsys.readouterr().out
    assert "500" in out
    assert "Already logged in" not in out


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


def test_create_session_flat_file_allows_first_named_session(
    sessions_creds_file, monkeypatch, capsys
):
    import json

    sessions_creds_file.write_text(
        json.dumps({"api_token": "tok", "cbrain_url": "http://localhost:3000", "user_id": 1})
    )
    monkeypatch.setattr("cbrain_cli.sessions.session_name", "prod")
    monkeypatch.setattr("cbrain_cli.sessions.session_specified", True)
    monkeypatch.setattr("builtins.input", lambda _: "admin")
    monkeypatch.setattr("getpass.getpass", lambda _: "secret")
    monkeypatch.setattr(
        "cbrain_cli.cli_utils.CbrainClient.post_form",
        lambda self, *_: {"cbrain_api_token": "newtok", "user_id": 1},
    )

    result = create_session(argparse.Namespace())
    assert result == 0
    saved = json.loads(sessions_creds_file.read_text())
    assert saved["prod"]["api_token"] == "newtok"
    assert saved["default"]["api_token"] == "tok"
    assert "Already logged in" not in capsys.readouterr().out


def test_list_sessions_no_credentials_file(sessions_creds_file, capsys):
    result = list_sessions(argparse.Namespace())
    assert result == 0
    assert "No saved sessions" in capsys.readouterr().out


def test_switch_session_no_credentials_file(sessions_creds_file, capsys):
    result = switch_session(argparse.Namespace(session_target="default"))
    assert result == 1
    assert "No saved sessions" in capsys.readouterr().out


def test_create_session_empty_username_arg_raises(sessions_creds_file):
    with pytest.raises(CliValidationError, match="[Uu]sername"):
        create_session(
            argparse.Namespace(server="http://localhost:3000", username="", password="x")
        )


def test_create_session_empty_server_arg_raises(sessions_creds_file):
    with pytest.raises(CliValidationError, match="[Ss]erver"):
        create_session(argparse.Namespace(server="", username="admin", password="x"))


def test_create_session_bad_password_reports_login_failure(
    monkeypatch, sessions_creds_file, capsys
):
    def _raise_401(self, *_a, **_k):
        raise CliApiError("Unauthorized", status=401)

    monkeypatch.setattr("cbrain_cli.cli_utils.CbrainClient.post_form", _raise_401)
    result = create_session(
        argparse.Namespace(server="http://127.0.0.1:3000", username="admin", password="wrong")
    )
    assert result == 1
    out = capsys.readouterr().out
    assert "Login failed" in out
    assert "Session expired" not in out


def test_create_session_unreachable_login_server_shows_url(
    monkeypatch, sessions_creds_file, capsys
):
    def _raise(self, *_a, **_k):
        raise urllib.error.URLError("Connection refused")

    monkeypatch.setattr("cbrain_cli.cli_utils.CbrainClient.post_form", _raise)
    result = create_session(
        argparse.Namespace(server="http://127.0.0.1:59999", username="admin", password="x")
    )
    assert result == 1
    assert "127.0.0.1:59999" in capsys.readouterr().out
