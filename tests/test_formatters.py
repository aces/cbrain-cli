from cbrain_cli.formatter import projects_fmt, tags_fmt, tasks_fmt
from tests.conftest import make_args, parse_json_output


def test_print_projects_list_empty_normal(capsys):
    projects_fmt.print_projects_list([], make_args())
    assert "No projects found." in capsys.readouterr().out


def test_print_projects_list_empty_json(capsys):
    projects_fmt.print_projects_list([], make_args(json=True))
    assert parse_json_output(capsys) == []


def test_print_projects_list_empty_jsonl(capsys):
    projects_fmt.print_projects_list([], make_args(jsonl=True))
    assert capsys.readouterr().out.strip() == ""


def test_print_projects_list_json(capsys):
    data = [{"id": 1, "type": "Group", "name": "Alpha"}]
    projects_fmt.print_projects_list(data, make_args(json=True))
    result = parse_json_output(capsys)
    assert result[0]["name"] == "Alpha"


def test_print_no_project_normal(capsys):
    projects_fmt.print_no_project(make_args())
    assert "No current project set" in capsys.readouterr().out


def test_print_no_project_json(capsys):
    projects_fmt.print_no_project(make_args(json=True))
    result = parse_json_output(capsys)
    assert result["current_group_id"] is None


def test_print_unswitch_result_json(capsys):
    result = {
        "previous_group_id": 5,
        "previous_group_name": "Alpha",
        "current_group_id": None,
    }
    projects_fmt.print_unswitch_result(result, make_args(json=True))
    parsed = parse_json_output(capsys)
    assert parsed["previous_group_id"] == 5


def test_print_task_data_empty_normal(capsys):
    tasks_fmt.print_task_data([], make_args())
    assert "No tasks found." in capsys.readouterr().out


def test_print_task_data_empty_json(capsys):
    tasks_fmt.print_task_data([], make_args(json=True))
    assert parse_json_output(capsys) == []


def test_print_task_data_json(capsys):
    data = [{"id": 2, "type": "BoutiquesTask::X", "status": "Done"}]
    tasks_fmt.print_task_data(data, make_args(json=True))
    result = parse_json_output(capsys)
    assert result[0]["id"] == 2


def test_print_task_details_json(capsys):
    data = {"id": 9, "type": "CbrainTask::Diagnostics", "status": "Ready"}
    tasks_fmt.print_task_details(data, make_args(json=True))
    result = parse_json_output(capsys)
    assert result["status"] == "Ready"


def test_print_tags_list_empty_normal(capsys):
    tags_fmt.print_tags_list([], make_args())
    assert "No tags found." in capsys.readouterr().out


def test_print_tags_list_empty_json(capsys):
    tags_fmt.print_tags_list([], make_args(json=True))
    assert parse_json_output(capsys) == []


def test_print_tags_list_json(capsys):
    data = [{"id": 1, "name": "mytag", "user_id": 2, "group_id": 3}]
    tags_fmt.print_tags_list(data, make_args(json=True))
    result = parse_json_output(capsys)
    assert result[0]["name"] == "mytag"


def test_print_tools_list_empty_normal(capsys):
    from cbrain_cli.formatter import tools_fmt

    tools_fmt.print_tools_list([], make_args())
    assert "No tools found." in capsys.readouterr().out


def test_print_tools_list_with_data(capsys):
    from cbrain_cli.formatter import tools_fmt

    data = [{"id": 1, "name": "T", "category": "C", "description": "desc"}]
    tools_fmt.print_tools_list(data, make_args())
    assert "Found 1 tools" in capsys.readouterr().out


def test_print_tool_details_normal(capsys):
    from cbrain_cli.formatter import tools_fmt

    tools_fmt.print_tool_details({"id": 1, "name": "T"}, make_args())
    assert "TOOL DETAILS" in capsys.readouterr().out


def test_print_files_list_empty(capsys):
    from cbrain_cli.formatter import files_fmt

    files_fmt.print_files_list([], make_args())
    assert "No files found." in capsys.readouterr().out


def test_print_file_details_with_flags(capsys):
    from cbrain_cli.formatter import files_fmt

    files_fmt.print_file_details(
        {"id": 1, "description": "d", "hidden": True, "immutable": True, "archived": True},
        make_args(),
    )
    out = capsys.readouterr().out
    assert "description: d" in out
    assert "hidden: True" in out


def test_print_upload_result_success(capsys):
    from cbrain_cli.formatter import files_fmt

    files_fmt.print_upload_result({"notice": "saved"}, 201, "f.txt", 12, 3)
    out = capsys.readouterr().out
    assert "uploaded successfully" in out
    assert "saved" in out


def test_print_move_copy_result_success(capsys):
    from cbrain_cli.formatter import files_fmt

    files_fmt.print_move_copy_result({"message": "queued", "background_activity_id": 9}, 200, "copy")
    out = capsys.readouterr().out
    assert "queued" in out
    assert "Background activity ID: 9" in out


def test_print_delete_result_normal(capsys):
    from cbrain_cli.formatter import files_fmt

    files_fmt.print_delete_result({"message": "deleted"}, make_args())
    assert "deleted" in capsys.readouterr().out


def test_print_providers_list_empty(capsys):
    from cbrain_cli.formatter import data_providers_fmt

    data_providers_fmt.print_providers_list([], make_args())
    assert "No data providers found." in capsys.readouterr().out


def test_print_provider_details_normal(capsys):
    from cbrain_cli.formatter import data_providers_fmt

    data_providers_fmt.print_provider_details({"id": 1, "name": "DP", "type": "Ssh"}, make_args())
    assert "DATA PROVIDER DETAILS" in capsys.readouterr().out


def test_print_tool_configs_list_empty(capsys):
    from cbrain_cli.formatter import tool_configs_fmt

    tool_configs_fmt.print_tool_configs_list([], make_args())
    assert "No tool configurations found." in capsys.readouterr().out


def test_print_tool_config_details_normal(capsys):
    from cbrain_cli.formatter import tool_configs_fmt

    tool_configs_fmt.print_tool_config_details({"id": 1, "description": "cfg"}, make_args())
    assert "id: 1" in capsys.readouterr().out


def test_print_boutiques_descriptor(capsys):
    from cbrain_cli.formatter import tool_configs_fmt

    tool_configs_fmt.print_boutiques_descriptor({"name": "Tool"}, make_args())
    assert '"name": "Tool"' in capsys.readouterr().out


def test_print_activities_list_with_data(capsys):
    from cbrain_cli.formatter import background_activities_fmt

    data = [
        {
            "id": 1,
            "user_id": 2,
            "remote_resource_id": 3,
            "status": "Done",
            "created_at": "2024-01-01T12:00:00.000Z",
            "items": [1, 2],
            "num_successes": 2,
            "num_failures": 0,
        }
    ]
    background_activities_fmt.print_activities_list(data, make_args())
    assert "Done" in capsys.readouterr().out


def test_print_activity_details_normal(capsys):
    from cbrain_cli.formatter import background_activities_fmt

    background_activities_fmt.print_activity_details({"id": 1, "status": "Done"}, make_args())
    assert "BACKGROUND ACTIVITY DETAILS" in capsys.readouterr().out


def test_print_resources_list_with_data(capsys):
    from cbrain_cli.formatter import remote_resources_fmt

    remote_resources_fmt.print_resources_list(
        [{"id": 1, "name": "rr", "online": True, "read_only": False}], make_args()
    )
    assert "REMOTE RESOURCES" in capsys.readouterr().out


def test_print_resource_details_normal(capsys):
    from cbrain_cli.formatter import remote_resources_fmt

    remote_resources_fmt.print_resource_details({"id": 1, "name": "rr"}, make_args())
    assert "REMOTE RESOURCE DETAILS" in capsys.readouterr().out


def test_print_tag_details_normal(capsys):
    tags_fmt.print_tag_details({"id": 1, "name": "t"}, make_args())
    assert "TAG DETAILS" in capsys.readouterr().out


def test_print_tag_operation_result_success(capsys):
    tags_fmt.print_tag_operation_result("create", success=True)
    assert "created successfully" in capsys.readouterr().out


def test_print_projects_list_with_data(capsys):
    projects_fmt.print_projects_list([{"id": 1, "type": "Group", "name": "A"}], make_args())
    assert "Group" in capsys.readouterr().out


def test_print_project_details_normal(capsys):
    projects_fmt.print_project_details({"id": 1, "name": "A", "description": "line1\nline2"}, make_args())
    out = capsys.readouterr().out
    assert "PROJECT DETAILS" in out
    assert "line1" in out


def test_print_unswitch_result_normal(capsys):
    projects_fmt.print_unswitch_result(
        {"previous_group_id": 5, "previous_group_name": "Alpha"}, make_args()
    )
    assert "Cleared current project" in capsys.readouterr().out


def test_print_task_data_normal_with_rows(capsys):
    tasks_fmt.print_task_data(
        [{"id": 1, "type": "BoutiquesTask::X", "status": "Done", "bourreau_id": 2, "user_id": 3, "group_id": 4}],
        make_args(),
    )
    assert "Total: 1 task(s)" in capsys.readouterr().out


def test_print_task_details_normal(capsys):
    tasks_fmt.print_task_details(
        {"id": 1, "type": "T", "status": "Ready", "description": "note", "params": {"k": "v"}},
        make_args(),
    )
    out = capsys.readouterr().out
    assert "Ready" in out
    assert "PARAMETERS" in out
