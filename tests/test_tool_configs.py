import pytest

from cbrain_cli.cli_utils import CliValidationError
from cbrain_cli.data.tool_configs import (
    list_tool_configs,
    show_tool_config,
    tool_config_boutiques_descriptor,
)
from tests.conftest import install_auth
from tests.conftest import make_args as _args


@pytest.fixture(autouse=True)
def _patch_locals():
    install_auth()


def test_list_tool_configs_returns_list(mock_urlopen):
    mock_urlopen([{"id": 1, "tool_id": 10}])
    result = list_tool_configs(_args())
    assert isinstance(result, list)
    assert result[0]["id"] == 1


def test_list_tool_configs_empty_list_is_not_error(mock_urlopen):
    mock_urlopen([])
    assert list_tool_configs(_args()) == []


def test_show_tool_config_missing_id_raises():
    with pytest.raises(CliValidationError):
        show_tool_config(_args(id=None))


def test_show_tool_config_returns_dict(mock_urlopen):
    mock_urlopen({"id": 3, "tool_id": 10})
    result = show_tool_config(_args(id=3))
    assert result["id"] == 3


def test_tool_config_boutiques_descriptor_missing_id_raises():
    with pytest.raises(CliValidationError):
        tool_config_boutiques_descriptor(_args(id=None))


def test_tool_config_boutiques_descriptor_returns_dict(mock_urlopen):
    mock_urlopen({"name": "MyTool", "schema-version": "0.5"})
    result = tool_config_boutiques_descriptor(_args(id=3))
    assert result["name"] == "MyTool"
