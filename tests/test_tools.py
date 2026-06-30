import json
from unittest.mock import MagicMock

import pytest

from cbrain_cli.cli_utils import CliApiError, CliValidationError
from cbrain_cli.data.tools import list_tools, show_tool
from tests.conftest import make_args
from tests.conftest import patch_module_locals


@pytest.fixture(autouse=True)
def _patch_tools_locals(monkeypatch):
    patch_module_locals(monkeypatch, "cbrain_cli.data.tools")


def test_list_tools_passes_page_and_per_page(monkeypatch):
    captured = {}

    def fake_urlopen(request):
        captured["url"] = request.full_url
        mock_http_response = MagicMock()
        mock_http_response.__enter__.return_value.read.return_value = b"[]"
        mock_http_response.__exit__.return_value = False
        return mock_http_response

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    list_tools(make_args(page=2, per_page=10))
    assert "page=2" in captured["url"]
    assert "per_page=10" in captured["url"]


def test_show_tool_missing_id_raises():
    with pytest.raises(CliValidationError):
        show_tool(make_args(id=None))


def test_show_tool_finds_tool_on_first_page(monkeypatch):
    mock_http_response = MagicMock()
    mock_http_response.__enter__.return_value.read.return_value = json.dumps(
        [{"id": 3, "name": "MyTool"}, {"id": 4, "name": "Other"}]
    ).encode()
    mock_http_response.__exit__.return_value = False
    monkeypatch.setattr("urllib.request.urlopen", MagicMock(return_value=mock_http_response))
    result = show_tool(make_args(id=3))
    assert result["id"] == 3
    assert result["name"] == "MyTool"


def test_show_tool_empty_first_page_raises_cli_api_error(monkeypatch):
    """Empty first page with no tools raises CliApiError instead of returning None."""
    mock_http_response = MagicMock()
    mock_http_response.__enter__.return_value.read.return_value = b"[]"
    mock_http_response.__exit__.return_value = False
    monkeypatch.setattr("urllib.request.urlopen", MagicMock(return_value=mock_http_response))
    with pytest.raises(CliApiError):
        show_tool(make_args(id=99))


def test_show_tool_stops_on_short_page(monkeypatch):
    """Short page (len < per_page) ends pagination without further requests."""
    # per_page inside show_tool is hardcoded 20; 1-item page > short-circuit
    mock_http_response = MagicMock()
    page_data = json.dumps([{"id": 10, "name": "X"}]).encode()
    mock_http_response.__enter__.return_value.read.return_value = page_data
    mock_http_response.__exit__.return_value = False
    mock_urlopen = MagicMock(return_value=mock_http_response)
    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)
    with pytest.raises(CliApiError):
        show_tool(make_args(id=99))
    assert mock_urlopen.call_count == 1


def test_show_tool_finds_tool_on_second_page(monkeypatch):
    first_page_items = [{"id": i, "name": f"T{i}"} for i in range(1, 21)]
    first_page = MagicMock()
    first_page.__enter__.return_value.read.return_value = json.dumps(first_page_items).encode()
    first_page.__exit__.return_value = False
    second_page = MagicMock()
    second_page.__enter__.return_value.read.return_value = json.dumps(
        [{"id": 99, "name": "Target"}]
    ).encode()
    second_page.__exit__.return_value = False
    monkeypatch.setattr(
        "urllib.request.urlopen",
        MagicMock(side_effect=[first_page, second_page]),
    )
    result = show_tool(make_args(id=99))
    assert result["name"] == "Target"
