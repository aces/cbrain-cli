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


def patch_credentials_file(monkeypatch, path, *, sessions=False):
    """Redirect credential file path away from the real ~/.config/cbrain."""
    monkeypatch.setattr("cbrain_cli.config.CREDENTIALS_FILE", path)
    if sessions:
        monkeypatch.setattr("cbrain_cli.sessions.CREDENTIALS_FILE", path)


def patch_module_locals(monkeypatch, *module_paths, user_id=None):
    """Patch module-local api_token / cbrain_url (and optional user_id) copies."""
    for module_path in module_paths:
        monkeypatch.setattr(f"{module_path}.api_token", TOKEN)
        monkeypatch.setattr(f"{module_path}.cbrain_url", URL)
        if user_id is not None:
            monkeypatch.setattr(f"{module_path}.user_id", user_id)


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


@pytest.fixture
def creds_file(tmp_path, monkeypatch):
    """Temp credentials file patched on cbrain_cli.config."""
    path = tmp_path / CREDS_FILE
    patch_credentials_file(monkeypatch, path)
    return path


@pytest.fixture
def sessions_creds_file(tmp_path, monkeypatch):
    """Temp credentials file patched on config and sessions modules."""
    path = tmp_path / CREDS_FILE
    patch_credentials_file(monkeypatch, path, sessions=True)
    return path


@pytest.fixture
def capture_urlopen(monkeypatch):
    """Patch urlopen and capture outgoing request details.

    Returns (configure, captured) where configure installs the mock and
    captured holds url, headers, data, and method from the last request.
    """

    def configure(response_json=None, status=200, raw_body=None, side_effect=None):
        def fake_urlopen(request):
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


@pytest.fixture(autouse=True)
def _reset_globals(monkeypatch):
    """Reset cli_utils module-level globals before every test.

    Prevents real credentials on disk from leaking into tests.
    """
    monkeypatch.setattr("cbrain_cli.cli_utils.api_token", None)
    monkeypatch.setattr("cbrain_cli.cli_utils.cbrain_url", None)
    monkeypatch.setattr("cbrain_cli.cli_utils.user_id", None)


@pytest.fixture
def fake_credentials(monkeypatch, _reset_globals):
    """Set known credentials on cbrain_cli.cli_utils globals.

    Explicit dependency on _reset_globals guarantees ordering — _reset_globals
    runs first (sets None), then this fixture overwrites with real values.

    Tests for data modules must ALSO patch the module-local copy, e.g.:
        patch_module_locals(monkeypatch, "cbrain_cli.data.tasks")
    """
    monkeypatch.setattr("cbrain_cli.cli_utils.api_token", TOKEN)
    monkeypatch.setattr("cbrain_cli.cli_utils.cbrain_url", URL)
    monkeypatch.setattr("cbrain_cli.cli_utils.user_id", 1)


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
