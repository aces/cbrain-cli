from cbrain_cli.main import build_parser


def test_build_parser_has_core_commands():
    parser, _command_parsers = build_parser()
    assert parser.parse_args(["logout"]).command == "logout"
    assert parser.parse_args(["version"]).command == "version"
    assert parser.parse_args(["task", "list"]).action == "list"
    assert parser.parse_args(["project", "unswitch"]).action == "unswitch"


def test_task_list_bourreau_id_args():
    parser, _command_parsers = build_parser()
    args = parser.parse_args(["task", "list", "bourreau-id", "7"])
    assert args.command == "task"
    assert args.action == "list"
    assert args.filter_name == "bourreau_id"
    assert args.bourreau_id == 7


def test_task_operation_args():
    parser, _command_parsers = build_parser()
    args = parser.parse_args(["task", "operation", "terminate", "--task-id", "1", "2", "--nozip"])
    assert args.action == "operation"
    assert args.operation == "terminate"
    assert args.task_id == [1, 2]
    assert args.nozip is True


def test_global_debug_flag():
    parser, _command_parsers = build_parser()
    args = parser.parse_args(["--debug", "task", "list"])
    assert args.debug is True


def test_file_list_kebab_options_normalize_to_snake_case():
    parser, _command_parsers = build_parser()
    args = parser.parse_args(
        [
            "file",
            "list",
            "--group-id",
            "5",
            "--data-provider-id",
            "9",
            "--file-type",
            "TextFile",
            "--per-page",
            "50",
        ]
    )
    assert args.group_id == 5
    assert args.dp_id == 9
    assert args.file_type == "TextFile"
    assert args.per_page == 50


def test_file_dp_id_aliases():
    parser, _command_parsers = build_parser()
    for flag in ("--data-provider-id", "--data-provider", "--dp-id"):
        args = parser.parse_args(["file", "list", flag, "3"])
        assert args.dp_id == 3


def test_file_upload_data_provider_aliases():
    parser, _command_parsers = build_parser()
    for flag in ("--data-provider-id", "--data-provider", "--dp-id"):
        args = parser.parse_args(["file", "upload", "/tmp/x", flag, "15"])
        assert args.data_provider == 15


def test_data_provider_command_and_alias():
    parser, _command_parsers = build_parser()
    canonical = parser.parse_args(["data-provider", "list"])
    alias = parser.parse_args(["dataprovider", "list"])
    assert canonical.command == "data-provider"
    assert alias.command == "dataprovider"
    assert canonical.action == alias.action == "list"


def test_tag_create_kebab_options_normalize_to_snake_case():
    parser, _command_parsers = build_parser()
    args = parser.parse_args(
        ["tag", "create", "--name", "demo", "--user-id", "1", "--group-id", "2"]
    )
    assert args.user_id == 1
    assert args.group_id == 2
    assert not hasattr(args, "user-id")
    assert not hasattr(args, "group-id")


def test_project_unswitch_subcommand():
    parser, _command_parsers = build_parser()
    args = parser.parse_args(["project", "unswitch"])
    assert args.command == "project"
    assert args.action == "unswitch"


def test_global_json_flag_on_task_list():
    parser, _command_parsers = build_parser()
    args = parser.parse_args(["--json", "task", "list"])
    assert args.json is True
    assert args.jsonl is False


def test_global_jsonl_flag_on_task_list():
    parser, _command_parsers = build_parser()
    args = parser.parse_args(["--jsonl", "task", "list"])
    assert args.jsonl is True
    assert args.json is False


def test_pagination_flags_on_file_list():
    parser, _command_parsers = build_parser()
    args = parser.parse_args(["file", "list", "--page", "2", "--per-page", "50"])
    assert args.page == 2
    assert args.per_page == 50


def test_pagination_flags_on_tool_list():
    parser, _command_parsers = build_parser()
    args = parser.parse_args(["tool", "list", "--page", "3", "--per-page", "100"])
    assert args.page == 3
    assert args.per_page == 100


def test_logout_command_sets_handler():
    parser, _command_parsers = build_parser()
    args = parser.parse_args(["logout"])
    assert args.command == "logout"
    assert callable(args.func)


def test_command_parsers_include_model_commands():
    _parser, command_parsers = build_parser()
    for command in (
        "file",
        "data-provider",
        "project",
        "tool",
        "tool-config",
        "tag",
        "background",
        "task",
        "remote-resource",
    ):
        assert command in command_parsers
