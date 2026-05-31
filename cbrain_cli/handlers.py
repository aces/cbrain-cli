"""
Command handlers for the CBRAIN CLI.

This module contains all the handler functions that process CLI commands
and format their output appropriately.
"""

from cbrain_cli.cli_utils import json_printer
from cbrain_cli.data import (
    background_activities,
    data_providers,
    files,
    projects,
    remote_resources,
    tags,
    tasks,
    tool_configs,
    tools,
)
from cbrain_cli.formatter import (
    background_activities_fmt,
    data_providers_fmt,
    files_fmt,
    projects_fmt,
    remote_resources_fmt,
    tags_fmt,
    tasks_fmt,
    tool_configs_fmt,
    tools_fmt,
)


# File command handlers
def handle_file_list(args):
    """
    Retrieve and display a paginated list of files from CBRAIN with optional filtering.
    """
    result = files.list_files(args)
    if result:
        files_fmt.print_files_list(result, args)


def handle_file_show(args):
    """
    Retrieve and display detailed information about a specific file by its ID.
    """
    result = files.show_file(args)
    if result:
        files_fmt.print_file_details(result, args)


def handle_file_upload(args):
    """Upload a local file to CBRAIN and display the upload result with file details."""
    result = files.upload_file(args)
    if result:
        files_fmt.print_upload_result(*result)


def handle_file_copy(args):
    """Copy one or more files to a different data provider and display the operation results."""
    result = files.copy_file(args)
    if result:
        files_fmt.print_move_copy_result(*result, operation="copy")


def handle_file_move(args):
    """Move one or more files to a different data provider and display the operation results."""
    result = files.move_file(args)
    if result:
        files_fmt.print_move_copy_result(*result, operation="move")


def handle_file_delete(args):
    """Delete a specific file from CBRAIN and display the deletion status."""
    result = files.delete_file(args)
    if result:
        files_fmt.print_delete_result(result, args)


# Data provider command handlers
def handle_dataprovider_list(args):
    """Retrieve and display a paginated list of available data providers in CBRAIN."""
    result = data_providers.list_data_providers(args)
    data_providers_fmt.print_providers_list(result, args)


def handle_dataprovider_show(args):
    """Retrieve and display detailed information about a specific data provider."""
    result = data_providers.show_data_provider(args)
    data_providers_fmt.print_provider_details(result, args)


def handle_dataprovider_is_alive(args):
    """Check and display the connectivity status of a specific data provider."""
    result = data_providers.is_alive(args)
    json_printer(result)


def handle_dataprovider_delete_unregistered(args):
    """Remove unregistered files from a data provider and display the cleanup results."""
    result = data_providers.delete_unregistered_files(args)
    json_printer(result)


# Project command handlers
def handle_project_list(args):
    """Retrieve and display a list of all available projects (groups) in CBRAIN."""
    result = projects.list_projects(args)
    projects_fmt.print_projects_list(result, args)


def handle_project_switch(args):
    """Switch the current working context to a different project and confirm the change."""
    result = projects.switch_project(args)
    if result:
        projects_fmt.print_current_project(result)


def handle_project_show(args):
    """Display information about the currently active project or a specific project by ID."""
    result = projects.show_project(args)
    if result:
        # Check if a specific project ID was requested
        project_id = getattr(args, "project_id", None)
        if project_id:
            # Show detailed project information for specific project
            projects_fmt.print_project_details(result, args)
        else:
            # Show current project information
            projects_fmt.print_current_project(result)
    else:
        # Only show "no project" message if no specific ID was requested
        project_id = getattr(args, "project_id", None)
        if not project_id:
            projects_fmt.print_no_project()


def handle_project_unswitch(args):
    """Unswitch from current project context."""
    print("Project Unswitch 'all' not yet implemented as of Aug 2025")


# Tool command handlers
def handle_tool_show(args):
    """Retrieve and display detailed information about a specific computational tool."""
    result = tools.list_tools(args)
    if result:
        tools_fmt.print_tool_details(result, args)


def handle_tool_list(args):
    """Retrieve and display a paginated list of available computational tools in CBRAIN."""
    result = tools.list_tools(args)
    if result:
        tools_fmt.print_tools_list(result, args)


# Tool config command handlers
def handle_tool_config_list(args):
    """Retrieve and display a paginated list of tool configurations available in CBRAIN."""
    result = tool_configs.list_tool_configs(args)
    tool_configs_fmt.print_tool_configs_list(result, args)


def handle_tool_config_show(args):
    """Retrieve and display detailed configuration settings for a specific tool."""
    result = tool_configs.show_tool_config(args)
    if result:
        tool_configs_fmt.print_tool_config_details(result, args)


def handle_tool_config_boutiques_descriptor(args):
    """Retrieve and display the Boutiques descriptor JSON for a specific tool configuration."""
    result = tool_configs.tool_config_boutiques_descriptor(args)
    if result:
        tool_configs_fmt.print_boutiques_descriptor(result, args)


# Tag command handlers
def handle_tag_list(args):
    """Retrieve and display a paginated list of tags available in CBRAIN."""
    result = tags.list_tags(args)
    tags_fmt.print_tags_list(result, args)


def handle_tag_show(args):
    """Retrieve and display detailed information about a specific tag by its ID."""
    result = tags.show_tag(args)
    if result:
        tags_fmt.print_tag_details(result, args)


def handle_tag_create(args):
    """Create a new tag with specified name, user, and group, then display the creation result."""
    result = tags.create_tag(args)
    if result:
        tags_fmt.print_tag_operation_result(
            "create", success=result[1], error_msg=result[2], response_status=result[3]
        )


def handle_tag_update(args):
    """Update an existing tag's properties and display the modification result."""
    result = tags.update_tag(args)
    if result:
        tags_fmt.print_tag_operation_result(
            "update",
            tag_id=args.tag_id,
            success=result[1],
            error_msg=result[2],
            response_status=result[3],
        )


def handle_tag_delete(args):
    """Delete a specific tag from CBRAIN and display the deletion result."""
    result = tags.delete_tag(args)
    if result:
        tags_fmt.print_tag_operation_result(
            "delete",
            tag_id=args.tag_id,
            success=result[0],
            error_msg=result[1],
            response_status=result[2],
        )


# Background activity command handlers
def handle_background_list(args):
    """Retrieve and display a list of background activities currently running in CBRAIN."""
    result = background_activities.list_background_activities(args)
    if result:
        background_activities_fmt.print_activities_list(result, args)


def handle_background_show(args):
    """Retrieve and display detailed information about a specific background activity."""
    result = background_activities.show_background_activity(args)
    if result:
        background_activities_fmt.print_activity_details(result, args)


# Task command handlers
def handle_task_list(args):
    """Retrieve and display a paginated list of computational tasks with optional filtering."""
    result = tasks.list_tasks(args)
    tasks_fmt.print_task_data(result, args)


def handle_task_show(args):
    """Retrieve and display detailed information about a specific computational task."""
    result = tasks.show_task(args)
    if result:
        tasks_fmt.print_task_details(result, args)


# Remote resource command handlers
def handle_remote_resource_list(args):
    """Retrieve and display a list of remote computational resources available in CBRAIN."""
    result = remote_resources.list_remote_resources(args)
    remote_resources_fmt.print_resources_list(result, args)


def handle_remote_resource_show(args):
    """Retrieve and display detailed information about a specific remote computational resource."""
    result = remote_resources.show_remote_resource(args)
    if result:
        remote_resources_fmt.print_resource_details(result, args)
