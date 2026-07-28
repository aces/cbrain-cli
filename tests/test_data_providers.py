import pytest

from cbrain_cli.cli_utils import CliApiError, CliValidationError
from cbrain_cli.data.data_providers import (
    delete_unregistered_files,
    is_alive,
    list_data_providers,
    show_data_provider,
)
from tests.conftest import install_auth
from tests.conftest import make_args as _args


@pytest.fixture(autouse=True)
def _patch_locals():
    install_auth()


def test_list_data_providers_returns_list(mock_urlopen):
    mock_urlopen([{"id": 1, "name": "LocalDP"}])
    result = list_data_providers(_args())
    assert isinstance(result, list)
    assert result[0]["id"] == 1


def test_list_data_providers_empty_list_is_not_error(mock_urlopen):
    mock_urlopen([])
    assert list_data_providers(_args()) == []


def test_show_data_provider_with_id_returns_dict(mock_urlopen):
    mock_urlopen({"id": 2, "name": "LocalDP"})
    result = show_data_provider(_args(id=2))
    assert result["id"] == 2


def test_show_data_provider_id_none_falls_back_to_list(capture_urlopen):
    """Missing id falls back to list_data_providers hits list endpoint, does not raise."""
    configure, captured = capture_urlopen
    configure(raw_body=b'[{"id": 1}, {"id": 2}]')
    result = show_data_provider(_args(id=None))
    assert isinstance(result, list)
    assert "/data_providers" in captured["url"]
    assert "/data_providers/" not in captured["url"].split("?")[0]


def test_show_data_provider_api_error_in_body_raises(mock_urlopen):
    mock_urlopen({"error": "Provider unavailable"})
    with pytest.raises(CliApiError, match="Provider unavailable"):
        show_data_provider(_args(id=5))


def test_is_alive_missing_id_raises():
    with pytest.raises(CliValidationError):
        is_alive(_args(id=None))


def test_is_alive_returns_result(mock_urlopen):
    mock_urlopen({"is_alive": True})
    result = is_alive(_args(id=1))
    assert result["is_alive"] is True


def test_delete_unregistered_files_missing_id_raises():
    with pytest.raises(CliValidationError):
        delete_unregistered_files(_args(id=None))


def test_delete_unregistered_files_returns_data(mock_urlopen):
    mock_urlopen({"removed": 3})
    result = delete_unregistered_files(_args(id=1))
    assert result["removed"] == 3
