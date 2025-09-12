"""
Setup and commands for the CBRAIN CLI command line interface.
"""

import argparse
import sys

from cbrain_cli.cli_utils import handle_errors, is_authenticated, version_info
from cbrain_cli.data.tasks import operation_task
from cbrain_cli.handlers import (
    handle_background_list,
    handle_background_show,
    handle_dataprovider_delete_unregistered,
    handle_dataprovider_is_alive,
    handle_dataprovider_list,
    handle_dataprovider_show,
    handle_file_copy,
    handle_file_delete,
    handle_file_list,
    handle_file_move,
    handle_file_show,
    handle_file_upload,
    handle_project_list,
    handle_project_show,
    handle_project_switch,
    handle_project_unswitch,
    handle_remote_resource_list,
    handle_remote_resource_show,
    handle_tag_create,
    handle_tag_delete,
    handle_tag_list,
    handle_tag_show,
    handle_tag_update,
    handle_task_list,
    handle_task_show,
    handle_tool_config_boutiques_descriptor,
    handle_tool_config_list,
    handle_tool_config_show,
    handle_tool_list,
    handle_tool_show,
)
from cbrain_cli.sessions import create_session, logout_session
from cbrain_cli.users import whoami_user


def main():
    """
    The function that controls the CBRAIN CLI.

    Returns
    -------
    None
        A command is run via inputs from the user.
    """
    parser = argparse.ArgumentParser(description="CBRAIN CLI")
    parser.add_argument("-j", "--json", action="store_true", help="Output in JSON format")
    parser.add_argument(
        "-jl",
        "--jsonl",
        action="store_true",
        help="Output in JSONL format (one JSON object per line)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Version command
    version_parser = subparsers.add_parser("version", help="Show CLI version")
    version_parser.set_defaults(func=handle_errors(version_info))

    # MARK: Session commands (top-level)
    # Create new session.
    login_parser = subparsers.add_parser("login", help="Login to CBRAIN")
    login_parser.set_defaults(func=handle_errors(create_session))

    # Logout session.
    logout_parser = subparsers.add_parser("logout", help="Logout from CBRAIN")
    logout_parser.set_defaults(func=handle_errors(logout_session))

    # Show current session.
    whoami_parser = subparsers.add_parser("whoami", help="Show current session")
    whoami_parser.add_argument("-v", "--version", action="store_true", help="Show version")
    whoami_parser.set_defaults(func=handle_errors(whoami_user))

    # MARK: Model-based commands
    # File commands
    file_parser = subparsers.add_parser("file", help="File operations")
    file_subparsers = file_parser.add_subparsers(dest="action", help="File actions")

    # file list
    file_list_parser = file_subparsers.add_parser("list", help="List files")
    file_list_parser.add_argument("--group-id", type=int, help="Filter files by group ID")
    file_list_parser.add_argument("--dp-id", type=int, help="Filter files by data provider ID")
    file_list_parser.add_argument("--user-id", type=int, help="Filter files by user ID")
    file_list_parser.add_argument("--parent-id", type=int, help="Filter files by parent ID")
    file_list_parser.add_argument("--file-type", type=str, help="Filter files by type")
    file_list_parser.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    file_list_parser.add_argument(
        "--per-page", type=int, default=25, help="Number of files per page (5-1000, default: 25)"
    )
    file_list_parser.set_defaults(func=handle_errors(handle_file_list))

    # file show
    file_show_parser = file_subparsers.add_parser("show", help="Show file details")
    file_show_parser.add_argument("file", type=int, help="File ID")
    file_show_parser.set_defaults(func=handle_errors(handle_file_show))

    # file upload
    file_upload_parser = file_subparsers.add_parser("upload", help="Upload a file to CBRAIN")
    file_upload_parser.add_argument("file_path", help="Path to the file to upload")
    file_upload_parser.add_argument(
        "--data-provider", type=int, required=True, help="Data provider ID"
    )
    file_upload_parser.add_argument("--group-id", type=int, help="Group ID")

    file_upload_parser.set_defaults(func=handle_errors(handle_file_upload))

    # file copy
    file_copy_parser = file_subparsers.add_parser(
        "copy", help="Copy files to another data provider"
    )
    file_copy_parser.add_argument(
        "--file-id",
        type=int,
        nargs="+",
        required=True,
        help="One or more file IDs to copy",
    )
    file_copy_parser.add_argument(
        "--dp-id", type=int, required=True, help="Destination data provider ID"
    )
    file_copy_parser.set_defaults(func=handle_errors(handle_file_copy))

    # file move
    file_move_parser = file_subparsers.add_parser(
        "move", help="Move files to another data provider"
    )
    file_move_parser.add_argument(
        "--file-id",
        type=int,
        nargs="+",
        required=True,
        help="One or more file IDs to move",
    )
    file_move_parser.add_argument(
        "--dp-id", type=int, required=True, help="Destination data provider ID"
    )
    file_move_parser.set_defaults(func=handle_errors(handle_file_move))

    # file delete
    file_delete_parser = file_subparsers.add_parser("delete", help="Delete a file")
    file_delete_parser.add_argument("file_id", type=int, help="ID of the file to delete")
    file_delete_parser.set_defaults(func=handle_errors(handle_file_delete))

    # Data provider commands
    dataprovider_parser = subparsers.add_parser("dataprovider", help="Data provider operations")
    dataprovider_subparsers = dataprovider_parser.add_subparsers(
        dest="action", help="Data provider actions"
    )

    # dataprovider list
    dataprovider_list_parser = dataprovider_subparsers.add_parser(
        "list", help="List data providers"
    )
    dataprovider_list_parser.set_defaults(func=handle_errors(handle_dataprovider_list))

    dataprovider_list_parser.add_argument(
        "--page", type=int, default=1, help="Page number (default: 1)"
    )
    dataprovider_list_parser.add_argument(
        "--per-page",
        type=int,
        default=25,
        help="Number of data providers per page (5-1000, default: 25)",
    )
    # dataprovider show
    dataprovider_show_parser = dataprovider_subparsers.add_parser(
        "show", help="Show data provider details"
    )
    dataprovider_show_parser.add_argument("id", type=int, help="Data provider ID")
    dataprovider_show_parser.set_defaults(func=handle_errors(handle_dataprovider_show))

    # dataprovider is_alive
    dataprovider_is_alive_parser = dataprovider_subparsers.add_parser(
        "is-alive", help="Check if a data provider is alive"
    )
    dataprovider_is_alive_parser.add_argument("id", type=int, help="Data provider ID")
    dataprovider_is_alive_parser.set_defaults(func=handle_errors(handle_dataprovider_is_alive))

    # dataprovider delete-unregistered-files
    dataprovider_delete_unregistered_files_parser = dataprovider_subparsers.add_parser(
        "delete-unregistered-files",
        help="Delete unregistered files from a data provider",
    )
    dataprovider_delete_unregistered_files_parser.add_argument(
        "id", type=int, help="Data provider ID"
    )
    dataprovider_delete_unregistered_files_parser.set_defaults(
        func=handle_errors(handle_dataprovider_delete_unregistered)
    )

    # Project commands
    project_parser = subparsers.add_parser("project", help="Project operations")
    project_subparsers = project_parser.add_subparsers(dest="action", help="Project actions")

    # project list
    project_list_parser = project_subparsers.add_parser("list", help="List projects")
    project_list_parser.set_defaults(func=handle_errors(handle_project_list))

    # project switch
    project_switch_parser = project_subparsers.add_parser("switch", help="Switch to a project")
    project_switch_parser.add_argument("group_id", help="Project/Group ID or 'all'")
    project_switch_parser.set_defaults(func=handle_errors(handle_project_switch))

    # project show
    project_show_parser = project_subparsers.add_parser(
        "show", help="Show current project or specific project by ID"
    )
    project_show_parser.add_argument(
        "project_id", type=int, nargs="?", help="Project ID to show (optional)"
    )
    project_show_parser.set_defaults(func=handle_errors(handle_project_show))

    # project unswitch
    project_unswitch_parser = project_subparsers.add_parser(
        "unswitch", help="Unswitch from current project"
    )
    project_unswitch_parser.set_defaults(func=handle_errors(handle_project_unswitch))

    # Tool commands
    tool_parser = subparsers.add_parser("tool", help="Tool operations")
    tool_subparsers = tool_parser.add_subparsers(dest="action", help="Tool actions")

    # tool show
    tool_show_parser = tool_subparsers.add_parser("show", help="Show tool details")
    tool_show_parser.add_argument("id", type=int, help="Tool ID")
    tool_show_parser.set_defaults(func=handle_errors(handle_tool_show))

    # tool list (reusing show_tool without id)
    tool_list_parser = tool_subparsers.add_parser("list", help="List all tools")
    tool_list_parser.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    tool_list_parser.add_argument(
        "--per-page", type=int, default=25, help="Number of tools per page (5-1000, default: 25)"
    )
    tool_list_parser.set_defaults(func=handle_errors(handle_tool_list))

    ## MARK: tool-config commands
    tool_configs_parser = subparsers.add_parser("tool-config", help="Tool configuration operations")
    tool_configs_subparsers = tool_configs_parser.add_subparsers(
        dest="action", help="Tool configuration actions"
    )

    # tool-config list
    tool_configs_list_parser = tool_configs_subparsers.add_parser(
        "list", help="List all tool configurations"
    )
    tool_configs_list_parser.set_defaults(func=handle_errors(handle_tool_config_list))

    tool_configs_list_parser.add_argument(
        "--page", type=int, default=1, help="Page number (default: 1)"
    )
    tool_configs_list_parser.add_argument(
        "--per-page",
        type=int,
        default=25,
        help="Number of tool configurations per page (5-1000, default: 25)",
    )

    # tool-config show
    tool_configs_show_parser = tool_configs_subparsers.add_parser(
        "show", help="Show tool configuration details"
    )
    tool_configs_show_parser.add_argument("id", type=int, help="Tool configuration ID")
    tool_configs_show_parser.set_defaults(func=handle_errors(handle_tool_config_show))

    # tool-config boutiques-descriptor
    tool_configs_boutiques_parser = tool_configs_subparsers.add_parser(
        "boutiques-descriptor", help="Get Boutiques descriptor for a tool configuration"
    )
    tool_configs_boutiques_parser.add_argument("id", type=int, help="Tool configuration ID")
    tool_configs_boutiques_parser.set_defaults(
        func=handle_errors(handle_tool_config_boutiques_descriptor)
    )

    # Tag commands
    tag_parser = subparsers.add_parser("tag", help="Tag operations")
    tag_subparsers = tag_parser.add_subparsers(dest="action", help="Tag actions")

    # tag list
    tag_list_parser = tag_subparsers.add_parser("list", help="List tags")
    tag_list_parser.set_defaults(func=handle_errors(handle_tag_list))

    tag_list_parser.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    tag_list_parser.add_argument(
        "--per-page", type=int, default=25, help="Number of tags per page (5-1000, default: 25)"
    )

    # tag show
    tag_show_parser = tag_subparsers.add_parser("show", help="Show tag details")
    tag_show_parser.add_argument("id", type=int, help="Tag ID")
    tag_show_parser.set_defaults(func=handle_errors(handle_tag_show))

    # tag create
    tag_create_parser = tag_subparsers.add_parser("create", help="Create a new tag")
    tag_create_parser.add_argument("--name", type=str, required=True, help="Tag name")
    tag_create_parser.add_argument("--user-id", type=int, required=True, help="User ID")
    tag_create_parser.add_argument("--group-id", type=int, required=True, help="Group ID")
    tag_create_parser.set_defaults(func=handle_errors(handle_tag_create))

    # tag update
    tag_update_parser = tag_subparsers.add_parser("update", help="Update an existing tag")
    tag_update_parser.add_argument(
        "tag_id",
        type=int,
        help="Tag ID to update",
    )
    tag_update_parser.add_argument("--name", type=str, required=True, help="Tag name")
    tag_update_parser.add_argument("--user-id", type=int, required=True, help="User ID")
    tag_update_parser.add_argument("--group-id", type=int, required=True, help="Group ID")
    tag_update_parser.set_defaults(func=handle_errors(handle_tag_update))

    # tag delete
    tag_delete_parser = tag_subparsers.add_parser("delete", help="Delete a tag")
    tag_delete_parser.add_argument(
        "tag_id",
        type=int,
        help="Tag ID to delete",
    )
    tag_delete_parser.set_defaults(func=handle_errors(handle_tag_delete))

    # Background activity commands
    background_parser = subparsers.add_parser("background", help="Background activity operations")
    background_subparsers = background_parser.add_subparsers(
        dest="action", help="Background activity actions"
    )

    # background list
    background_list_parser = background_subparsers.add_parser(
        "list", help="List background activities"
    )
    background_list_parser.set_defaults(func=handle_errors(handle_background_list))

    # background show
    background_show_parser = background_subparsers.add_parser(
        "show", help="Show background activity details"
    )
    background_show_parser.add_argument("id", type=int, help="Background activity ID")
    background_show_parser.set_defaults(func=handle_errors(handle_background_show))

    # Task commands
    task_parser = subparsers.add_parser("task", help="Task operations")
    task_subparsers = task_parser.add_subparsers(dest="action", help="Task actions")

    # task list
    task_list_parser = task_subparsers.add_parser("list", help="List tasks")
    task_list_parser.add_argument(
        "filter_type", nargs="?", choices=["bourreau-id"], help="Filter type (optional)"
    )
    task_list_parser.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    task_list_parser.add_argument(
        "--per-page", type=int, default=25, help="Number of tasks per page (5-1000, default: 25)"
    )
    task_list_parser.add_argument(
        "filter_value",
        type=int,
        nargs="?",
        help="Filter value (required if filter_type is specified)",
    )
    task_list_parser.set_defaults(func=handle_errors(handle_task_list))

    # task show
    task_show_parser = task_subparsers.add_parser("show", help="Show task details")
    task_show_parser.add_argument("task", type=int, help="Task ID")
    task_show_parser.set_defaults(func=handle_errors(handle_task_show))

    # task operation
    task_operation_parser = task_subparsers.add_parser("operation", help="operation on a task")
    task_operation_parser.set_defaults(func=handle_errors(operation_task))

    # Remote resource commands
    remote_resource_parser = subparsers.add_parser(
        "remote-resource", help="Remote resource operations"
    )
    remote_resource_subparsers = remote_resource_parser.add_subparsers(
        dest="action", help="Remote resource actions"
    )

    # remote-resource list
    remote_resource_list_parser = remote_resource_subparsers.add_parser(
        "list", help="List remote resources"
    )
    remote_resource_list_parser.set_defaults(func=handle_errors(handle_remote_resource_list))

    # remote-resource show
    remote_resource_show_parser = remote_resource_subparsers.add_parser(
        "show", help="Show remote resource details"
    )
    remote_resource_show_parser.add_argument("remote_resource", type=int, help="Remote resource ID")
    remote_resource_show_parser.set_defaults(func=handle_errors(handle_remote_resource_show))

    # MARK: Setup CLI
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Handle session commands (no authentication needed for login, version, and whoami).
    if args.command == "login":
        return handle_errors(create_session)(args)
    elif args.command == "version":
        return handle_errors(version_info)(args)
    elif args.command == "whoami":
        return handle_errors(whoami_user)(args)

    # All other commands require authentication.
    if not is_authenticated():
        return 1

    # Handle authenticated commands.
    if args.command == "logout":
        return handle_errors(logout_session)(args)
    elif args.command in [
        "file",
        "dataprovider",
        "project",
        "tool",
        "tool-config",
        "tag",
        "background",
        "task",
        "remote-resource",
    ]:
        if not hasattr(args, "action") or not args.action:
            # Show help for the specific model command.
            if args.command == "file":
                file_parser.print_help()
            elif args.command == "dataprovider":
                dataprovider_parser.print_help()
            elif args.command == "project":
                project_parser.print_help()
            elif args.command == "tool":
                tool_parser.print_help()
            elif args.command == "tool-config":
                tool_configs_parser.print_help()
            elif args.command == "tag":
                tag_parser.print_help()
            elif args.command == "background":
                background_parser.print_help()
            elif args.command == "task":
                task_parser.print_help()
            elif args.command == "remote-resource":
                remote_resource_parser.print_help()
            return 1
        else:
            # Execute the function associated with the command.
            return args.func(args)

    # If we get here, something went wrong.
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
