"""
Command handlers for the CBRAIN CLI.

This module contains all the handler functions that process CLI commands
and format their output appropriately.
"""

from cbrain_cli.cli_utils import json_printer
from cbrain_cli.data.background_activities import (
    list_background_activities,
    show_background_activity,
)
from cbrain_cli.data.data_providers import (
    delete_unregistered_files,
    is_alive,
    list_data_providers,
    show_data_provider,
)
from cbrain_cli.data.files import (
    copy_file,
    delete_file,
    list_files,
    move_file,
    show_file,
    upload_file,
)
from cbrain_cli.data.projects import list_projects, show_project, switch_project
from cbrain_cli.data.remote_resources import list_remote_resources, show_remote_resource
from cbrain_cli.data.tags import create_tag, delete_tag, list_tags, show_tag, update_tag
from cbrain_cli.data.tasks import list_tasks, show_task
from cbrain_cli.data.tool_configs import (
    list_tool_configs,
    show_tool_config,
    tool_config_boutiques_descriptor,
)
from cbrain_cli.data.tools import list_tools
from cbrain_cli.formatter.background_activities_fmt import (
    print_activities_list,
    print_activity_details,
)
from cbrain_cli.formatter.data_providers_fmt import print_provider_details, print_providers_list
from cbrain_cli.formatter.files_fmt import (
    print_delete_result,
    print_file_details,
    print_files_list,
    print_move_copy_result,
    print_upload_result,
)
from cbrain_cli.formatter.projects_fmt import (
    print_current_project,
    print_no_project,
    print_projects_list,
)
from cbrain_cli.formatter.remote_resources_fmt import print_resource_details, print_resources_list
from cbrain_cli.formatter.tags_fmt import (
    print_tag_details,
    print_tag_operation_result,
    print_tags_list,
)
from cbrain_cli.formatter.tasks_fmt import print_task_data, print_task_details
from cbrain_cli.formatter.tool_configs_fmt import (
    print_boutiques_descriptor,
    print_tool_config_details,
    print_tool_configs_list,
)
from cbrain_cli.formatter.tools_fmt import print_tool_details, print_tools_list


# File command handlers
def handle_file_list(args):
    """
    Retrieve and display a paginated list of files from CBRAIN with optional filtering.
    """
    result = list_files(args)
    if result:
        print_files_list(result, args)


def handle_file_show(args):
    """
    Retrieve and display detailed information about a specific file by its ID.
    """
    result = show_file(args)
    if result:
        print_file_details(result, args)


def handle_file_upload(args):
    """Upload a local file to CBRAIN and display the upload result with file details."""
    result = upload_file(args)
    if result:
        print_upload_result(*result)


def handle_file_copy(args):
    """Copy one or more files to a different data provider and display the operation results."""
    result = copy_file(args)
    if result:
        print_move_copy_result(*result, operation="copy")


def handle_file_move(args):
    """Move one or more files to a different data provider and display the operation results."""
    result = move_file(args)
    if result:
        print_move_copy_result(*result, operation="move")


def handle_file_delete(args):
    """Delete a specific file from CBRAIN and display the deletion status."""
    result = delete_file(args)
    if result:
        print_delete_result(result, args)


# Data provider command handlers
def handle_dataprovider_list(args):
    """Retrieve and display a paginated list of available data providers in CBRAIN."""
    result = list_data_providers(args)
    print_providers_list(result, args)


def handle_dataprovider_show(args):
    """Retrieve and display detailed information about a specific data provider."""
    result = show_data_provider(args)
    print_provider_details(result, args)


def handle_dataprovider_is_alive(args):
    """Check and display the connectivity status of a specific data provider."""
    result = is_alive(args)
    json_printer(result)


def handle_dataprovider_delete_unregistered(args):
    """Remove unregistered files from a data provider and display the cleanup results."""
    result = delete_unregistered_files(args)
    json_printer(result)


# Project command handlers
def handle_project_list(args):
    """Retrieve and display a list of all available projects (groups) in CBRAIN."""
    result = list_projects(args)
    print_projects_list(result, args)


def handle_project_switch(args):
    """Switch the current working context to a different project and confirm the change."""
    result = switch_project(args)
    if result:
        print_current_project(result)


def handle_project_show(args):
    """Display information about the currently active project or a specific project by ID."""
    result = show_project(args)
    if result:
        # Check if a specific project ID was requested
        project_id = getattr(args, "project_id", None)
        if project_id:
            # Show detailed project information for specific project
            from cbrain_cli.formatter.projects_fmt import print_project_details

            print_project_details(result, args)
        else:
            # Show current project information
            print_current_project(result)
    else:
        # Only show "no project" message if no specific ID was requested
        project_id = getattr(args, "project_id", None)
        if not project_id:
            print_no_project()


def handle_project_unswitch(args):
    """Unswitch from current project context."""
    print("Project Unswitch 'all' not yet implemented as of Aug 2025")


# Tool command handlers
def handle_tool_show(args):
    """Retrieve and display detailed information about a specific computational tool."""
    result = list_tools(args)
    if result:
        print_tool_details(result, args)


def handle_tool_list(args):
    """Retrieve and display a paginated list of available computational tools in CBRAIN."""
    result = list_tools(args)
    if result:
        print_tools_list(result, args)


# Tool config command handlers
def handle_tool_config_list(args):
    """Retrieve and display a paginated list of tool configurations available in CBRAIN."""
    result = list_tool_configs(args)
    print_tool_configs_list(result, args)


def handle_tool_config_show(args):
    """Retrieve and display detailed configuration settings for a specific tool."""
    result = show_tool_config(args)
    if result:
        print_tool_config_details(result, args)


def handle_tool_config_boutiques_descriptor(args):
    """Retrieve and display the Boutiques descriptor JSON for a specific tool configuration."""
    result = tool_config_boutiques_descriptor(args)
    if result:
        print_boutiques_descriptor(result, args)


# Tag command handlers
def handle_tag_list(args):
    """Retrieve and display a paginated list of tags available in CBRAIN."""
    result = list_tags(args)
    print_tags_list(result, args)


def handle_tag_show(args):
    """Retrieve and display detailed information about a specific tag by its ID."""
    result = show_tag(args)
    if result:
        print_tag_details(result, args)


def handle_tag_create(args):
    """Create a new tag with specified name, user, and group, then display the creation result."""
    result = create_tag(args)
    if result:
        print_tag_operation_result(
            "create", success=result[1], error_msg=result[2], response_status=result[3]
        )


def handle_tag_update(args):
    """Update an existing tag's properties and display the modification result."""
    result = update_tag(args)
    if result:
        print_tag_operation_result(
            "update",
            tag_id=args.tag_id,
            success=result[1],
            error_msg=result[2],
            response_status=result[3],
        )


def handle_tag_delete(args):
    """Delete a specific tag from CBRAIN and display the deletion result."""
    result = delete_tag(args)
    if result:
        print_tag_operation_result(
            "delete",
            tag_id=args.tag_id,
            success=result[0],
            error_msg=result[1],
            response_status=result[2],
        )


# Background activity command handlers
def handle_background_list(args):
    """Retrieve and display a list of background activities currently running in CBRAIN."""
    result = list_background_activities(args)
    if result:
        print_activities_list(result, args)


def handle_background_show(args):
    """Retrieve and display detailed information about a specific background activity."""
    result = show_background_activity(args)
    if result:
        print_activity_details(result, args)


# Task command handlers
def handle_task_list(args):
    """Retrieve and display a paginated list of computational tasks with optional filtering."""
    result = list_tasks(args)
    print_task_data(result, args)


def handle_task_show(args):
    """Retrieve and display detailed information about a specific computational task."""
    result = show_task(args)
    if result:
        print_task_details(result, args)


# Remote resource command handlers
def handle_remote_resource_list(args):
    """Retrieve and display a list of remote computational resources available in CBRAIN."""
    result = list_remote_resources(args)
    print_resources_list(result, args)


def handle_remote_resource_show(args):
    """Retrieve and display detailed information about a specific remote computational resource."""
    result = show_remote_resource(args)
    if result:
        print_resource_details(result, args)
