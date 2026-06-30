from unittest.mock import MagicMock

import pytest

import cbrain_cli.handlers as handlers
from cbrain_cli.cli_utils import CliValidationError, handle_errors
from cbrain_cli.handlers import (
    handle_project_switch,
    handle_project_unswitch,
    handle_task_list,
    handle_task_show,
)
from cbrain_cli.users import user_details, whoami_user
from tests.conftest import make_args, parse_json_output, patch_module_locals

LIST_HANDLER_CASES = [
    (
        "handle_file_list",
        "cbrain_cli.handlers.files.list_files",
        "cbrain_cli.handlers.files_fmt.print_files_list",
    ),
    (
        "handle_dataprovider_list",
        "cbrain_cli.handlers.data_providers.list_data_providers",
        "cbrain_cli.handlers.data_providers_fmt.print_providers_list",
    ),
    (
        "handle_project_list",
        "cbrain_cli.handlers.projects.list_projects",
        "cbrain_cli.handlers.projects_fmt.print_projects_list",
    ),
    (
        "handle_tool_list",
        "cbrain_cli.handlers.tools.list_tools",
        "cbrain_cli.handlers.tools_fmt.print_tools_list",
    ),
    (
        "handle_tool_config_list",
        "cbrain_cli.handlers.tool_configs.list_tool_configs",
        "cbrain_cli.handlers.tool_configs_fmt.print_tool_configs_list",
    ),
    (
        "handle_tag_list",
        "cbrain_cli.handlers.tags.list_tags",
        "cbrain_cli.handlers.tags_fmt.print_tags_list",
    ),
    (
        "handle_background_list",
        "cbrain_cli.handlers.background_activities.list_background_activities",
        "cbrain_cli.handlers.background_activities_fmt.print_activities_list",
    ),
    (
        "handle_task_list",
        "cbrain_cli.handlers.tasks.list_tasks",
        "cbrain_cli.handlers.tasks_fmt.print_task_data",
    ),
    (
        "handle_remote_resource_list",
        "cbrain_cli.handlers.remote_resources.list_remote_resources",
        "cbrain_cli.handlers.remote_resources_fmt.print_resources_list",
    ),
]


@pytest.mark.parametrize("handler_name,list_fn,fmt_fn", LIST_HANDLER_CASES)
def test_list_handler_empty_list_returns_none(monkeypatch, capsys, handler_name, list_fn, fmt_fn):
    """[] is not None — formatter must be called and must not return 1."""
    monkeypatch.setattr(list_fn, lambda _: [])
    monkeypatch.setattr(fmt_fn, lambda result, args: print("FORMATTED"))
    result = getattr(handlers, handler_name)(make_args())
    assert result is None
    assert "FORMATTED" in capsys.readouterr().out


@pytest.mark.parametrize("handler_name,list_fn,fmt_fn", LIST_HANDLER_CASES)
def test_list_handler_none_returns_1(monkeypatch, handler_name, list_fn, fmt_fn):
    fmt_called = []
    monkeypatch.setattr(list_fn, lambda _: None)
    monkeypatch.setattr(fmt_fn, lambda *args: fmt_called.append(True))
    assert getattr(handlers, handler_name)(make_args()) == 1
    assert fmt_called == []


def test_handle_task_list_returns_none_on_success(monkeypatch):
    monkeypatch.setattr("cbrain_cli.handlers.tasks.list_tasks", lambda _: [{"id": 1}])
    monkeypatch.setattr("cbrain_cli.handlers.tasks_fmt.print_task_data", lambda *_: None)
    assert handle_task_list(make_args()) is None


def test_handle_project_show_no_project_prints_message(monkeypatch, capsys):
    """show_project returning None with no project_id prints 'no project' message, not 1."""
    monkeypatch.setattr("cbrain_cli.handlers.projects.show_project", lambda _: None)
    monkeypatch.setattr(
        "cbrain_cli.handlers.projects_fmt.print_no_project",
        lambda args: print("No active project."),
    )
    from cbrain_cli.handlers import handle_project_show

    result = handle_project_show(make_args(project_id=None))
    assert result is None
    assert "No active project." in capsys.readouterr().out


def test_handle_project_unswitch_always_returns_none(monkeypatch):
    monkeypatch.setattr("cbrain_cli.handlers.projects.unswitch_project", lambda _: None)
    monkeypatch.setattr("cbrain_cli.handlers.projects_fmt.print_unswitch_result", lambda *_: None)
    assert handle_project_unswitch(make_args()) is None


def test_handle_project_switch_json_output(monkeypatch, capsys):
    monkeypatch.setattr(
        "cbrain_cli.handlers.projects.switch_project",
        lambda _: {"id": 5, "name": "Alpha"},
    )
    handle_project_switch(make_args(json=True, group_id="5"))
    assert parse_json_output(capsys)["id"] == 5


def test_handle_project_unswitch_json_output(monkeypatch, capsys):
    monkeypatch.setattr(
        "cbrain_cli.handlers.projects.unswitch_project",
        lambda _: {"previous_group_id": 5, "current_group_id": None},
    )
    handle_project_unswitch(make_args(json=True))
    assert parse_json_output(capsys)["current_group_id"] is None


def test_handle_task_show_success_returns_none(monkeypatch):
    monkeypatch.setattr(
        "cbrain_cli.handlers.tasks.show_task",
        lambda _: {"id": 2, "status": "Ready"},
    )
    monkeypatch.setattr("cbrain_cli.handlers.tasks_fmt.print_task_details", lambda *_: None)
    assert handle_task_show(make_args(task=2)) is None


def test_handle_task_show_none_returns_1(monkeypatch):
    monkeypatch.setattr("cbrain_cli.handlers.tasks.show_task", lambda _: None)
    fmt_called = []
    monkeypatch.setattr(
        "cbrain_cli.handlers.tasks_fmt.print_task_details",
        lambda *_: fmt_called.append(True),
    )
    assert handle_task_show(make_args(task=2)) == 1
    assert fmt_called == []


def test_list_handler_validation_error_returns_1(monkeypatch):
    monkeypatch.setattr(
        "cbrain_cli.handlers.tasks.list_tasks",
        MagicMock(side_effect=CliValidationError("bad filter")),
    )
    assert handle_errors(handle_task_list)(make_args()) == 1


def test_user_details_sends_current_token_in_header(monkeypatch, capture_urlopen):
    """auth_headers(api_token) is called inside user_details, not at import time."""
    patch_module_locals(monkeypatch, "cbrain_cli.users")
    monkeypatch.setattr("cbrain_cli.users.api_token", "new-token")

    configure, captured = capture_urlopen
    configure({"id": 1, "login": "admin"})
    user_details(1)

    assert captured["headers"].get("Authorization") == "Bearer new-token"


def test_whoami_user_version_does_not_print_debug_lines(monkeypatch, capsys):
    """whoami_user with version=True must not print DEBUG: lines."""
    patch_module_locals(monkeypatch, "cbrain_cli.users", user_id=1)

    monkeypatch.setattr(
        "cbrain_cli.users.user_details",
        lambda _: {"id": 1, "login": "admin", "full_name": "Admin"},
    )

    mock_http_response = MagicMock()
    mock_http_response.__enter__.return_value.read.return_value = (
        b'{"user_id": 1, "cbrain_api_token": "test-token"}'
    )
    mock_http_response.__exit__.return_value = False
    monkeypatch.setattr("urllib.request.urlopen", MagicMock(return_value=mock_http_response))

    whoami_user(make_args(version=True))

    out = capsys.readouterr().out
    assert "DEBUG:" not in out
