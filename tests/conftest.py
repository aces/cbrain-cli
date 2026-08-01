import argparse
import json
import sys
from unittest.mock import MagicMock

import pytest

URL = "http://localhost:3000"
TOKEN = "test-token"
CREDS_FILE = "creds.json"


def make_args(**kwargs):
    """Build an argparse.Namespace with default page/per_page; override with kwargs."""
    defaults = {"page": 1, "per_page": 25}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def patch_credentials_file(monkeypatch, path):
    """Redirect credential file path away from the real ~/.config/cbrain."""
    monkeypatch.setattr("cbrain_cli.config.CREDENTIALS_FILE", path)


def write_auth_credentials(path, *, user_id=42, **overrides):
    """Write call-time auth credentials into an isolated credentials file."""
    credentials = {"api_token": TOKEN, "cbrain_url": URL, "user_id": user_id}
    credentials.update(overrides)
    path.write_text(json.dumps(credentials))
    return credentials


def install_auth(*, user_id=None):
    """Write auth credentials so CbrainClient.from_credentials() picks them up."""
    from cbrain_cli import config

    uid = 42 if user_id is None else user_id
    write_auth_credentials(config.CREDENTIALS_FILE, user_id=uid)


def sample_credentials(**overrides):
    """Build a credentials dict with sensible defaults for tests."""
    credentials = {"api_token": TOKEN, "cbrain_url": URL, "user_id": 42}
    credentials.update(overrides)
    return credentials


def run_main(monkeypatch, argv):
    """Run cbrain_cli.main.main with the given argv list (including program name)."""
    monkeypatch.setattr(sys, "argv", argv)
    from cbrain_cli.main import main

    return main(argv[1:])


def parse_json_output(capsys):
    """Return stdout parsed as JSON."""
    return json.loads(capsys.readouterr().out.strip())


@pytest.fixture(autouse=True)
def _isolate_credentials(tmp_path, monkeypatch):
    """Redirect credentials file so real home config never leaks into tests."""
    path = tmp_path / CREDS_FILE
    patch_credentials_file(monkeypatch, path)
    return path


@pytest.fixture
def creds_file(_isolate_credentials):
    """Temp credentials file patched on cbrain_cli.config."""
    return _isolate_credentials


@pytest.fixture
def sessions_creds_file(_isolate_credentials):
    """Alias of the isolated credentials file used by session tests."""
    return _isolate_credentials


@pytest.fixture
def capture_urlopen(monkeypatch):
    """Patch urlopen and capture outgoing request details.

    Returns (configure, captured) where configure installs the mock and
    captured holds url, headers, data, and method from the last request.
    """

    def configure(response_json=None, status=200, raw_body=None, side_effect=None):
        def fake_urlopen(request, **kwargs):
            captured["url"] = request.full_url
            captured["headers"] = request.headers
            captured["data"] = request.data
            captured["method"] = request.method
            mock_http_response = MagicMock()
            if raw_body is not None:
                body = raw_body
            elif response_json is not None:
                body = json.dumps(response_json).encode()
            else:
                body = b"{}"
            mock_http_response.__enter__.return_value.read.return_value = body
            mock_http_response.__enter__.return_value.status = status
            mock_http_response.__exit__.return_value = False
            return mock_http_response

        if side_effect is not None:
            monkeypatch.setattr("urllib.request.urlopen", MagicMock(side_effect=side_effect))
        else:
            monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    captured = {}
    return configure, captured


@pytest.fixture
def fake_credentials(_isolate_credentials):
    """Write known credentials so CbrainClient.from_credentials() / is_authenticated() see them."""
    write_auth_credentials(_isolate_credentials, user_id=1)


@pytest.fixture
def mock_urlopen(monkeypatch):
    """Patch urllib.request.urlopen with a single-response MagicMock.

    Returns a callable configure_mock_response(response_json, status=200) that installs the mock.
    MagicMock chaining handles the context-manager protocol automatically.

    For sequential calls (e.g. switch_project: api_send then api_get),
    build context managers directly in the test instead:

        first_http_response, second_http_response = MagicMock(), MagicMock()
        first_http_response.__enter__.return_value.read.return_value = b'{}'
        first_http_response.__enter__.return_value.status = 200
        second_http_response.__enter__.return_value.read.return_value = json.dumps({...}).encode()
        second_http_response.__enter__.return_value.status = 200
        monkeypatch.setattr(
            "urllib.request.urlopen",
            MagicMock(side_effect=[first_http_response, second_http_response]),
        )
    """

    def configure_mock_response(response_json, status=200):
        mock_http_response = MagicMock()
        mock_http_response.__enter__.return_value.read.return_value = json.dumps(
            response_json
        ).encode()
        mock_http_response.__enter__.return_value.status = status
        monkeypatch.setattr("urllib.request.urlopen", MagicMock(return_value=mock_http_response))

    return configure_mock_response
