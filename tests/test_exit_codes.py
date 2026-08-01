import io
import json
import socket
from unittest.mock import MagicMock
from urllib.error import HTTPError, URLError

import pytest

from cbrain_cli.cli_utils import (
    CliApiError,
    CliResponseError,
    CliValidationError,
    get_status_code_description,
    handle_connection_error,
    handle_errors,
    is_authenticated,
)
from tests.conftest import URL, run_main


@pytest.mark.parametrize(
    "exc",
    [
        HTTPError(URL, 404, "Not Found", {}, None),
        URLError("timeout"),
        json.JSONDecodeError("err", "", 0),
        CliValidationError("bad input"),
        CliApiError("api fail"),
    ],
)
def test_handle_errors_returns_1_on_exception(exc):
    assert handle_errors(MagicMock(side_effect=exc))() == 1


def test_handle_errors_preserves_return_value():
    assert handle_errors(MagicMock(return_value=42))() == 42


@pytest.mark.parametrize(
    "code,expected",
    [
        (401, "Authentication error (401)"),
        (403, "Access forbidden (403)"),
        (404, "Resource not found (404)"),
        (500, "Server error (500)"),
    ],
)
def test_handle_connection_error_http(code, expected, capsys):
    # io.BytesIO(b"") ensures read() returns b"" reliably (fp=None triggers AttributeError)
    handle_connection_error(HTTPError(URL, code, "Err", {}, io.BytesIO(b"")))
    assert expected in capsys.readouterr().out


def test_handle_connection_error_url_error_connection_refused(fake_credentials, capsys):
    handle_connection_error(URLError("Connection refused"))
    assert "Cannot connect to CBRAIN server" in capsys.readouterr().out


def test_is_authenticated_false_when_no_credentials():
    assert is_authenticated() is False


def test_is_authenticated_false_when_cbrain_url_is_none(creds_file):
    creds_file.write_text(json.dumps({"api_token": "tok", "user_id": 1}))
    assert is_authenticated() is False


def test_is_authenticated_true_with_fake_credentials(fake_credentials):
    assert is_authenticated() is True


def test_main_file_list_unauthenticated_returns_1(monkeypatch, capsys):
    result = run_main(monkeypatch, ["cbrain", "file", "list"])
    assert result == 1
    assert "Not logged in" in capsys.readouterr().out


def test_main_version_bypasses_auth_check(monkeypatch):
    """version command must NOT call is_authenticated."""
    auth_checks = []
    monkeypatch.setattr(
        "cbrain_cli.main.is_authenticated",
        lambda: auth_checks.append(True) or True,
    )
    run_main(monkeypatch, ["cbrain", "version"])
    assert auth_checks == []


@pytest.mark.parametrize(
    "code,expected",
    [
        (422, "Validation error (422)"),
        (418, "Client error (418)"),
        (502, "Server error (502)"),
        (301, "HTTP error (301)"),
    ],
)
def test_get_status_code_description(code, expected):
    assert get_status_code_description(code) == expected


def test_handle_connection_error_401(capsys):
    handle_connection_error(HTTPError(URL, 401, "Unauthorized", {}, io.BytesIO(b"")))
    out = capsys.readouterr().out
    assert "Authentication error (401)" in out
    assert "authorized credentials" in out


def test_handle_connection_error_json_body(capsys):
    body = json.dumps({"message": "bad request"}).encode()
    handle_connection_error(HTTPError(URL, 400, "Bad Request", {}, io.BytesIO(body)))
    assert "bad request" in capsys.readouterr().out


def test_handle_connection_error_change_password_redirect(capsys):
    body = json.dumps({"error": "redirect change_password required"}).encode()
    handle_connection_error(HTTPError(URL, 400, "Bad Request", {}, io.BytesIO(body)))
    out = capsys.readouterr().out
    assert "password change" in out


def test_handle_connection_error_html_body(capsys):
    body = b"<header><h1>Not Found</h1></header><h2>Record missing</h2>"
    handle_connection_error(HTTPError(URL, 404, "Not Found", {}, io.BytesIO(body)))
    out = capsys.readouterr().out
    assert "Not Found" in out
    assert "Record missing" in out


def test_handle_connection_error_timeout(capsys):
    handle_connection_error(URLError(socket.timeout("timed out")))
    assert "timed out" in capsys.readouterr().out


def test_handle_errors_bare_read_timeout(capsys):
    result = handle_errors(MagicMock(side_effect=socket.timeout("timed out")))()
    assert result == 1
    assert "timed out" in capsys.readouterr().out


def test_handle_connection_error_generic_url_error(capsys):
    handle_connection_error(URLError("timed out"))
    assert "Connection failed" in capsys.readouterr().out


def test_handle_connection_error_non_http_error(capsys):
    handle_connection_error(RuntimeError("boom"))
    assert "Connection error: boom" in capsys.readouterr().out


def test_handle_errors_cli_response_error(capsys):
    def boom(_args):
        raise CliResponseError("bad response")

    assert handle_errors(boom)(MagicMock()) == 1
    assert "bad response" in capsys.readouterr().out


def test_handle_errors_keyboard_interrupt(capsys):
    def boom(_args):
        raise KeyboardInterrupt

    assert handle_errors(boom)(MagicMock()) == 1
    assert "cancelled" in capsys.readouterr().out


def test_handle_errors_unexpected_exception(capsys):
    def boom(_args):
        raise RuntimeError("unexpected")

    assert handle_errors(boom)(MagicMock()) == 1
    assert "unexpected" in capsys.readouterr().out
