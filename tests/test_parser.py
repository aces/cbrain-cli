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
    assert args.filter_name == "bourreau-id"
    assert args.bourreau_id == 7


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
        "dataprovider",
        "project",
        "tool",
        "tool-config",
        "tag",
        "background",
        "task",
        "remote-resource",
    ):
        assert command in command_parsers
