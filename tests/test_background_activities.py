import pytest

from cbrain_cli.cli_utils import CliValidationError
from cbrain_cli.data.background_activities import (
    list_background_activities,
    show_background_activity,
)
from tests.conftest import make_args as _args
from tests.conftest import patch_module_locals


@pytest.fixture(autouse=True)
def _patch_locals(monkeypatch):
    patch_module_locals(monkeypatch, "cbrain_cli.data.background_activities")


def test_list_background_activities_returns_list(mock_urlopen):
    mock_urlopen([{"id": 1, "type": "CleanupJob"}])
    result = list_background_activities(_args())
    assert isinstance(result, list)
    assert result[0]["id"] == 1


def test_list_background_activities_empty_list_is_not_error(mock_urlopen):
    """Empty list response must not raise — empty-list regression."""
    mock_urlopen([])
    assert list_background_activities(_args()) == []


def test_show_background_activity_missing_id_raises():
    with pytest.raises(CliValidationError):
        show_background_activity(_args(id=None))


def test_show_background_activity_returns_dict(mock_urlopen):
    mock_urlopen({"id": 5, "type": "CleanupJob", "status": "Completed"})
    result = show_background_activity(_args(id=5))
    assert result["id"] == 5
