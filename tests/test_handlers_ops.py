import pytest

import cbrain_cli.handlers as handlers
from tests.conftest import make_args

SHOW_HANDLER_CASES = [
    (
        "handle_file_show",
        "cbrain_cli.handlers.files.show_file",
        "cbrain_cli.handlers.files_fmt.print_file_details",
        {"id": 1, "name": "f.txt"},
        {"file": 1},
    ),
    (
        "handle_dataprovider_show",
        "cbrain_cli.handlers.data_providers.show_data_provider",
        "cbrain_cli.handlers.data_providers_fmt.print_provider_details",
        {"id": 2, "name": "LocalDP"},
        {"id": 2},
    ),
    (
        "handle_tool_show",
        "cbrain_cli.handlers.tools.show_tool",
        "cbrain_cli.handlers.tools_fmt.print_tool_details",
        {"id": 3, "name": "Tool"},
        {"id": 3},
    ),
    (
        "handle_tool_config_show",
        "cbrain_cli.handlers.tool_configs.show_tool_config",
        "cbrain_cli.handlers.tool_configs_fmt.print_tool_config_details",
        {"id": 4, "tool_id": 1},
        {"id": 4},
    ),
    (
        "handle_tag_show",
        "cbrain_cli.handlers.tags.show_tag",
        "cbrain_cli.handlers.tags_fmt.print_tag_details",
        {"id": 5, "name": "tag"},
        {"id": 5},
    ),
    (
        "handle_background_show",
        "cbrain_cli.handlers.background_activities.show_background_activity",
        "cbrain_cli.handlers.background_activities_fmt.print_activity_details",
        {"id": 6, "status": "Done"},
        {"id": 6},
    ),
    (
        "handle_remote_resource_show",
        "cbrain_cli.handlers.remote_resources.show_remote_resource",
        "cbrain_cli.handlers.remote_resources_fmt.print_resource_details",
        {"id": 7, "name": "rr"},
        {"remote_resource": 7},
    ),
]

FILE_UPLOAD_CASES = [
    (({"error": "fail"}, 400, "f.txt", 10, 1), 1),
    (({"notice": "ok"}, 201, "f.txt", 10, 1), None),
]

TAG_HANDLER_CASES = [
    (
        "handle_tag_create",
        "cbrain_cli.handlers.tags.create_tag",
        "cbrain_cli.handlers.tags_fmt.print_tag_operation_result",
        make_args(),
        (None, False, "bad", 422),
        1,
    ),
    (
        "handle_tag_create",
        "cbrain_cli.handlers.tags.create_tag",
        "cbrain_cli.handlers.tags_fmt.print_tag_operation_result",
        make_args(),
        ({"id": 1}, True, None, 201),
        None,
    ),
    (
        "handle_tag_update",
        "cbrain_cli.handlers.tags.update_tag",
        "cbrain_cli.handlers.tags_fmt.print_tag_operation_result",
        make_args(tag_id=1),
        (None, False, "bad", 422),
        1,
    ),
    (
        "handle_tag_delete",
        "cbrain_cli.handlers.tags.delete_tag",
        "cbrain_cli.handlers.tags_fmt.print_tag_operation_result",
        make_args(tag_id=1, yes=True),
        (True, None, 200),
        None,
    ),
]


def test_handle_dataprovider_is_alive_prints_json(monkeypatch, capsys):
    monkeypatch.setattr(
        "cbrain_cli.handlers.data_providers.is_alive",
        lambda _: {"alive": True},
    )
    handlers.handle_dataprovider_is_alive(make_args(id=1))
    assert '"alive": true' in capsys.readouterr().out


def test_handle_dataprovider_is_alive_none_returns_1(monkeypatch):
    monkeypatch.setattr("cbrain_cli.handlers.data_providers.is_alive", lambda _: None)
    assert handlers.handle_dataprovider_is_alive(make_args(id=1)) == 1


def test_handle_dataprovider_delete_unregistered_prints_json(monkeypatch, capsys):
    monkeypatch.setattr(
        "cbrain_cli.handlers.data_providers.delete_unregistered_files",
        lambda _: {"deleted": 2},
    )
    handlers.handle_dataprovider_delete_unregistered(make_args(id=1, yes=True))
    assert '"deleted": 2' in capsys.readouterr().out


def test_handle_project_show_with_id(monkeypatch, capsys):
    monkeypatch.setattr(
        "cbrain_cli.handlers.projects.show_project",
        lambda _: {"id": 9, "name": "Proj", "type": "Group"},
    )
    handlers.handle_project_show(make_args(project_id=9))
    assert "PROJECT DETAILS" in capsys.readouterr().out


def test_handle_project_switch_none_returns_1(monkeypatch):
    monkeypatch.setattr("cbrain_cli.handlers.projects.switch_project", lambda _: None)
    assert handlers.handle_project_switch(make_args(group_id="5")) == 1


@pytest.mark.parametrize("upload_result,expected", FILE_UPLOAD_CASES)
def test_handle_file_upload(monkeypatch, upload_result, expected):
    monkeypatch.setattr("cbrain_cli.handlers.files.upload_file", lambda _: upload_result)
    monkeypatch.setattr("cbrain_cli.handlers.files_fmt.print_upload_result", lambda *_, **__: None)
    result = handlers.handle_file_upload(make_args())
    assert result is expected if expected is None else result == expected


@pytest.mark.parametrize("handler,data_fn,fmt_fn,args,api_result,expected", TAG_HANDLER_CASES)
def test_tag_handlers(monkeypatch, handler, data_fn, fmt_fn, args, api_result, expected):
    monkeypatch.setattr(data_fn, lambda _: api_result)
    monkeypatch.setattr(fmt_fn, lambda *_, **__: None)
    result = getattr(handlers, handler)(args)
    assert result is expected if expected is None else result == expected


def test_handle_file_copy_failure_returns_1(monkeypatch):
    monkeypatch.setattr(
        "cbrain_cli.handlers.files.copy_file",
        lambda _: ({"error": "fail"}, 400),
    )
    monkeypatch.setattr(
        "cbrain_cli.handlers.files_fmt.print_move_copy_result", lambda *_, **__: None
    )
    assert handlers.handle_file_copy(make_args()) == 1


def test_handle_file_delete_success(monkeypatch):
    monkeypatch.setattr(
        "cbrain_cli.handlers.files.delete_file",
        lambda _: {"deleted": 1},
    )
    monkeypatch.setattr("cbrain_cli.handlers.files_fmt.print_delete_result", lambda *_: None)
    assert handlers.handle_file_delete(make_args(file_id=1, yes=True)) is None


def test_handle_file_delete_aborts_without_yes(monkeypatch):
    called = []
    monkeypatch.setattr(
        "cbrain_cli.handlers.files.delete_file",
        lambda _: called.append(True) or {"deleted": 1},
    )
    monkeypatch.setattr(
        "cbrain_cli.handlers.confirm_destructive",
        lambda *_: False,
    )
    assert handlers.handle_file_delete(make_args(file_id=1)) == 1
    assert called == []


def test_handle_tool_config_boutiques_descriptor(monkeypatch, capsys):
    monkeypatch.setattr(
        "cbrain_cli.handlers.tool_configs.tool_config_boutiques_descriptor",
        lambda _: {"name": "Tool"},
    )
    handlers.handle_tool_config_boutiques_descriptor(make_args(id=1))
    assert '"name": "Tool"' in capsys.readouterr().out


@pytest.mark.parametrize("handler_name,data_fn,fmt_fn,sample,arg_kwargs", SHOW_HANDLER_CASES)
def test_show_handler_success(
    monkeypatch, capsys, handler_name, data_fn, fmt_fn, sample, arg_kwargs
):
    monkeypatch.setattr(data_fn, lambda _: sample)
    getattr(handlers, handler_name)(make_args(**arg_kwargs))
    assert capsys.readouterr().out


@pytest.mark.parametrize("handler_name,data_fn,fmt_fn,sample,arg_kwargs", SHOW_HANDLER_CASES)
def test_show_handler_none_returns_1(
    monkeypatch, handler_name, data_fn, fmt_fn, sample, arg_kwargs
):
    fmt_called = []
    monkeypatch.setattr(data_fn, lambda _: None)
    monkeypatch.setattr(fmt_fn, lambda *_: fmt_called.append(True))
    assert getattr(handlers, handler_name)(make_args(**arg_kwargs)) == 1
    assert fmt_called == []
