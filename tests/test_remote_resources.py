import pytest

from cbrain_cli.cli_utils import CliValidationError
from cbrain_cli.data.remote_resources import list_remote_resources, show_remote_resource
from tests.conftest import install_auth
from tests.conftest import make_args as _args


@pytest.fixture(autouse=True)
def _patch_locals():
    install_auth()


def test_list_remote_resources_returns_list(mock_urlopen):
    mock_urlopen([{"id": 1, "name": "mainbrain"}])
    result = list_remote_resources(_args())
    assert isinstance(result, list)
    assert result[0]["id"] == 1


def test_list_remote_resources_empty_list_is_not_error(mock_urlopen):
    mock_urlopen([])
    assert list_remote_resources(_args()) == []


def test_show_remote_resource_missing_id_raises():
    with pytest.raises(CliValidationError):
        show_remote_resource(_args(remote_resource=None))


def test_show_remote_resource_returns_dict(mock_urlopen):
    mock_urlopen({"id": 3, "name": "mainbrain", "online": True})
    result = show_remote_resource(_args(remote_resource=3))
    assert result["id"] == 3
