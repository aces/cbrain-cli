import json
import urllib.error
from unittest.mock import MagicMock

import pytest

from cbrain_cli.cli_utils import CliApiError, CliValidationError
from cbrain_cli.data.projects import list_projects, show_project, switch_project, unswitch_project
from tests.conftest import TOKEN, URL, install_auth, make_args


@pytest.fixture(autouse=True)
def _patch_projects_locals():
    """Write auth credentials so CbrainClient.from_credentials() picks them up."""
    install_auth()


def test_list_projects_returns_list(mock_urlopen):
    mock_urlopen([{"id": 1, "name": "Project A"}])
    result = list_projects(make_args())
    assert isinstance(result, list)
    assert result[0]["id"] == 1


def test_list_projects_empty_list_is_not_error(mock_urlopen):
    """[] response is valid — empty list regression."""
    mock_urlopen([])
    assert list_projects(make_args()) == []


def test_show_project_no_credentials_returns_none(creds_file):
    result = show_project(make_args(project_id=None))
    assert result is None


def test_show_project_by_id_http_404_raises_cli_api_error(monkeypatch):
    """HTTP 404 on project lookup is converted to CliApiError."""
    monkeypatch.setattr(
        "urllib.request.urlopen",
        MagicMock(side_effect=urllib.error.HTTPError(URL, 404, "Not Found", {}, None)),
    )
    with pytest.raises(CliApiError, match="Project with ID 5 not found"):
        show_project(make_args(project_id=5))


def test_show_project_no_current_group_returns_none(creds_file):
    creds_file.write_text(json.dumps({"api_token": TOKEN}))
    result = show_project(make_args(project_id=None))
    assert result is None


def test_show_project_stale_group_raises_and_cleans_credentials(monkeypatch, creds_file):
    """When saved current_group_id returns 404, credentials cleaned and CliApiError raised."""
    from tests.conftest import write_auth_credentials

    write_auth_credentials(creds_file, current_group_id=99)
    monkeypatch.setattr(
        "urllib.request.urlopen",
        MagicMock(side_effect=urllib.error.HTTPError(URL, 404, "Not Found", {}, None)),
    )
    with pytest.raises(CliApiError):
        show_project(make_args(project_id=None))
    saved = json.loads(creds_file.read_text())
    assert "current_group_id" not in saved


def test_switch_project_missing_group_id_raises():
    with pytest.raises(CliValidationError):
        switch_project(make_args(group_id=None))


def test_switch_project_all_raises():
    with pytest.raises(CliValidationError):
        switch_project(make_args(group_id="all"))


def test_switch_project_invalid_string_raises():
    with pytest.raises(CliValidationError, match="[Ii]nvalid"):
        switch_project(make_args(group_id="abc"))


def test_switch_project_saves_credentials(monkeypatch, creds_file):
    from tests.conftest import write_auth_credentials

    write_auth_credentials(creds_file)

    session_delete_response = MagicMock()
    session_delete_response.__enter__.return_value.read.return_value = b""
    session_delete_response.__enter__.return_value.status = 200
    project_details_response = MagicMock()
    project_details_response.__enter__.return_value.read.return_value = json.dumps(
        {"id": 5, "name": "MyGroup"}
    ).encode()
    project_details_response.__enter__.return_value.status = 200
    monkeypatch.setattr(
        "urllib.request.urlopen",
        MagicMock(side_effect=[session_delete_response, project_details_response]),
    )

    result = switch_project(make_args(group_id="5"))
    assert result["id"] == 5
    saved = json.loads(creds_file.read_text())
    assert saved["current_group_id"] == 5


def test_unswitch_project_removes_group_from_credentials(creds_file, mock_urlopen):
    from tests.conftest import write_auth_credentials

    write_auth_credentials(creds_file, current_group_id=5, current_group_name="G")
    mock_urlopen({})
    result = unswitch_project(make_args())
    assert result["current_group_id"] is None
    saved = json.loads(creds_file.read_text())
    assert "current_group_id" not in saved
