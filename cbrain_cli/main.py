"""
Setup and commands for the CBRAIN CLI command line interface.
"""

import argparse
import sys

from cbrain_cli.cli_utils import handle_errors, is_authenticated
from cbrain_cli.dataProviders import show_data_provider, is_alive, delete_unregistered_files
from cbrain_cli.files import show_file, upload_file, copy_file, move_file
from cbrain_cli.list import list_data_providers, list_files, list_projects, list_background_activitites, show_background_activity
from cbrain_cli.projects import switch_project, show_project
from cbrain_cli.sessions import create_session, logout_session
from cbrain_cli.tags import create_tag, show_tag, list_tags, update_tag, delete_tag
from cbrain_cli.tool import show_tool
from cbrain_cli.version import whoami_user
from cbrain_cli.task import list_tasks, show_task, operation_task
from cbrain_cli.remote_resources import list_remote_resources, show_remote_resource

def main():
    """
    The function that controls the CBRAIN CLI.

    Returns
    -------
    None
        A command is ran via inputs from the user.
    """
    parser = argparse.ArgumentParser(description="CBRAIN CLI")
    parser.add_argument(
        "-j", "--json", action="store_true", help="Output in JSON format"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # MARK: Session commands (top-level)
    # Create new session.
    login_parser = subparsers.add_parser("login", help="Login to CBRAIN")
    login_parser.set_defaults(func=handle_errors(create_session))

    # Logout session.
    logout_parser = subparsers.add_parser("logout", help="Logout from CBRAIN")
    logout_parser.set_defaults(func=handle_errors(logout_session))

    # Show current session.
    whoami_parser = subparsers.add_parser("whoami", help="Show current session")
    whoami_parser.add_argument(
        "-v", "--version", action="store_true", help="Show version"
    )
    whoami_parser.set_defaults(func=handle_errors(whoami_user))

    # MARK: Model-based commands
    # File commands
    file_parser = subparsers.add_parser("file", help="File operations")
    file_subparsers = file_parser.add_subparsers(dest="action", help="File actions")
    
    # file list
    file_list_parser = file_subparsers.add_parser("list", help="List files")
    file_list_parser.add_argument("--group_id", type=int, help="Filter files by group ID")
    file_list_parser.add_argument("--data_provider_id", type=int, help="Filter files by data provider ID")
    file_list_parser.add_argument("--user_id", type=int, help="Filter files by user ID")
    file_list_parser.add_argument("--parent_id", type=int, help="Filter files by parent ID")
    file_list_parser.add_argument("--file_type", type=str, help="Filter files by type")
    file_list_parser.set_defaults(func=handle_errors(list_files))
    
    # file show
    file_show_parser = file_subparsers.add_parser("show", help="Show file details")
    file_show_parser.add_argument("file", type=int, help="File ID")
    file_show_parser.set_defaults(func=handle_errors(show_file))
    
    # file upload
    file_upload_parser = file_subparsers.add_parser("upload", help="Upload a file to CBRAIN")
    file_upload_parser.add_argument("file_path", help="Path to the file to upload")
    file_upload_parser.add_argument("--data-provider", type=int, required=True, help="Data provider ID")
    file_upload_parser.add_argument("--group-id", type=int, default=2, help="Group ID (default: 2)")
    file_upload_parser.add_argument("--TextFile", action="store_const", const="TextFile", dest="file_type", help="Upload as TextFile")
    file_upload_parser.add_argument("--SingleFile", action="store_const", const="SingleFile", dest="file_type", help="Upload as SingleFile")
    file_upload_parser.add_argument("--FileCollection", action="store_const", const="FileCollection", dest="file_type", help="Upload as FileCollection")
    file_upload_parser.set_defaults(func=handle_errors(upload_file))
    
    # file copy
    file_copy_parser = file_subparsers.add_parser("copy", help="Copy a file to another data provider")
    file_copy_parser.add_argument("--file_id", type=int, required=True, help="File ID to copy")
    file_copy_parser.add_argument("--data_provider_id_for_mv_cp", type=int, required=True, help="Destination data provider ID")
    file_copy_parser.set_defaults(func=handle_errors(copy_file))
    
    # file move
    file_move_parser = file_subparsers.add_parser("move", help="Move a file to another data provider")
    file_move_parser.add_argument("--file_id", type=int, required=True, help="File ID to move")
    file_move_parser.add_argument("--data_provider_id_for_mv_cp", type=int, required=True, help="Destination data provider ID")
    file_move_parser.set_defaults(func=handle_errors(move_file))

    # Data provider commands
    dataprovider_parser = subparsers.add_parser("dataprovider", help="Data provider operations")
    dataprovider_subparsers = dataprovider_parser.add_subparsers(dest="action", help="Data provider actions")
    
    # dataprovider list
    dataprovider_list_parser = dataprovider_subparsers.add_parser("list", help="List data providers")
    dataprovider_list_parser.set_defaults(func=handle_errors(list_data_providers))
    
    # dataprovider show
    dataprovider_show_parser = dataprovider_subparsers.add_parser("show", help="Show data provider details")
    dataprovider_show_parser.add_argument("id", type=int, help="Data provider ID")
    dataprovider_show_parser.set_defaults(func=handle_errors(show_data_provider))

    # dataprovider is_alive
    dataprovider_is_alive_parser = dataprovider_subparsers.add_parser("is_alive", help="Check if a data provider is alive")
    dataprovider_is_alive_parser.add_argument("id", type=int, help="Data provider ID")
    dataprovider_is_alive_parser.set_defaults(func=handle_errors(is_alive))

    # dataprovider delete_unregistered_files
    dataprovider_delete_unregistered_files_parser = dataprovider_subparsers.add_parser("delete_unregistered_files", help="Delete unregistered files from a data provider")
    dataprovider_delete_unregistered_files_parser.add_argument("id", type=int, help="Data provider ID")
    dataprovider_delete_unregistered_files_parser.set_defaults(func=handle_errors(delete_unregistered_files))

    # Project commands
    project_parser = subparsers.add_parser("project", help="Project operations")
    project_subparsers = project_parser.add_subparsers(dest="action", help="Project actions")
    
    # project list
    project_list_parser = project_subparsers.add_parser("list", help="List projects")
    project_list_parser.set_defaults(func=handle_errors(list_projects))
    
    # project switch
    project_switch_parser = project_subparsers.add_parser("switch", help="Switch to a project")
    project_switch_parser.add_argument("group_id", type=int, help="Project/Group ID")
    project_switch_parser.set_defaults(func=handle_errors(switch_project))
    
    # project show
    project_show_parser = project_subparsers.add_parser("show", help="Show current project")
    project_show_parser.set_defaults(func=handle_errors(show_project))

    # Tool commands
    tool_parser = subparsers.add_parser("tool", help="Tool operations")
    tool_subparsers = tool_parser.add_subparsers(dest="action", help="Tool actions")
    
    # tool show
    tool_show_parser = tool_subparsers.add_parser("show", help="Show tool details")
    tool_show_parser.add_argument("id", type=int, help="Tool ID")
    tool_show_parser.set_defaults(func=handle_errors(show_tool))

    # Tag commands
    tag_parser = subparsers.add_parser("tag", help="Tag operations")
    tag_subparsers = tag_parser.add_subparsers(dest="action", help="Tag actions")
    
    # tag list
    tag_list_parser = tag_subparsers.add_parser("list", help="List tags")
    tag_list_parser.set_defaults(func=handle_errors(list_tags))
    
    # tag show
    tag_show_parser = tag_subparsers.add_parser("show", help="Show tag details")
    tag_show_parser.add_argument("id", type=int, help="Tag ID")
    tag_show_parser.set_defaults(func=handle_errors(show_tag))
    
    # tag create
    tag_create_parser = tag_subparsers.add_parser("create", help="Create a new tag (interactive)")
    tag_create_parser.set_defaults(func=handle_errors(create_tag))
    
    # tag update
    tag_update_parser = tag_subparsers.add_parser("update", help="Update an existing tag (interactive)")
    tag_update_parser.set_defaults(func=handle_errors(update_tag))
    
    # tag delete
    tag_delete_parser = tag_subparsers.add_parser("delete", help="Delete a tag (interactive)")
    tag_delete_parser.set_defaults(func=handle_errors(delete_tag))

    # Background activity commands
    background_parser = subparsers.add_parser("background", help="Background activity operations")
    background_subparsers = background_parser.add_subparsers(dest="action", help="Background activity actions")
    
    # background list
    background_list_parser = background_subparsers.add_parser("list", help="List background activities")
    background_list_parser.set_defaults(func=handle_errors(list_background_activitites))
    
    # background show
    background_show_parser = background_subparsers.add_parser("show", help="Show background activity details")
    background_show_parser.add_argument("id", type=int, help="Background activity ID")
    background_show_parser.set_defaults(func=handle_errors(show_background_activity))

    # Task commands
    task_parser = subparsers.add_parser("task", help="Task operations")
    task_subparsers = task_parser.add_subparsers(dest="action", help="Task actions")
    
    # task list
    task_list_parser = task_subparsers.add_parser("list", help="List tasks")
    task_list_parser.add_argument("filter_type", nargs='?', choices=['bourreau_id'], help="Filter type (optional)")
    task_list_parser.add_argument("filter_value", type=int, nargs='?', help="Filter value (required if filter_type is specified)")
    task_list_parser.set_defaults(func=handle_errors(list_tasks))
    
    # task show
    task_show_parser = task_subparsers.add_parser("show", help="Show task details")
    task_show_parser.add_argument("task", type=int, help="Task ID")
    task_show_parser.set_defaults(func=handle_errors(show_task))

    # task operation
    task_operation_parser = task_subparsers.add_parser("operation", help="operation on a task")
    task_operation_parser.set_defaults(func=handle_errors(operation_task))

    # Remote resources commands (plural for listing)
    remote_resources_parser = subparsers.add_parser("remote_resources", help="Remote resources operations")
    remote_resources_subparsers = remote_resources_parser.add_subparsers(dest="action", help="Remote resources actions")
    
    # remote_resources list
    remote_resources_list_parser = remote_resources_subparsers.add_parser("list", help="List remote resources")
    remote_resources_list_parser.set_defaults(func=handle_errors(list_remote_resources))

    # Remote resource commands (singular for show)
    remote_resource_parser = subparsers.add_parser("remote_resource", help="Remote resource operations")
    remote_resource_subparsers = remote_resource_parser.add_subparsers(dest="action", help="Remote resource actions")
    
    # remote_resource show
    remote_resource_show_parser = remote_resource_subparsers.add_parser("show", help="Show remote resource details")
    remote_resource_show_parser.add_argument("remote_resource", type=int, help="Remote resource ID")
    remote_resource_show_parser.set_defaults(func=handle_errors(show_remote_resource))

    # MARK: Setup CLI
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Handle session commands (no authentication needed for login).
    if args.command == "login":
        return handle_errors(create_session)(args)

    # All other commands require authentication.
    if not is_authenticated():       
        return 1

    # Handle authenticated commands.
    if args.command == "logout":
        return handle_errors(logout_session)(args)
    elif args.command == "whoami":
        return handle_errors(whoami_user)(args)
    elif args.command in ["file", "dataprovider", "project", "tool", "tag", "background", "task", "remote_resources", "remote_resource"]:
        if not hasattr(args, 'action') or not args.action:
            # Show help for the specific model command.
            if args.command == "file":
                file_parser.print_help()
            elif args.command == "dataprovider":
                dataprovider_parser.print_help()
            elif args.command == "project":
                project_parser.print_help()
            elif args.command == "tool":
                tool_parser.print_help()
            elif args.command == "tag":
                tag_parser.print_help()
            elif args.command == "background":
                background_parser.print_help()
            elif args.command == "task":
                task_parser.print_help()
            elif args.command == "remote_resources":
                remote_resources_parser.print_help()
            elif args.command == "remote_resource":
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
