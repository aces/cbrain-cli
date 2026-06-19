import urllib.error

from cbrain_cli.cli_utils import (
    CliApiError,
    CliValidationError,
    api_get,
    api_send,
    api_token,
    cbrain_url,
)
from cbrain_cli.config import load_credentials, save_credentials


def switch_project(args):
    """
    Switch to a specific project/group and save it to credentials.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the group_id argument

    Returns
    -------
    dict or None
        Dictionary containing project details if successful, None otherwise
    """
    # Get the group ID from the group_id argument
    group_id = getattr(args, "group_id", None)
    if not group_id:
        raise CliValidationError("Group ID is required", field="group_id")

    if group_id == "all":
        raise CliValidationError(
            "Project switch 'all' not yet implemented as of Aug 2025", field="group_id"
        )

    try:
        group_id = int(group_id)
    except ValueError:
        raise CliValidationError(
            f"Invalid group ID '{group_id}'. Must be a number or 'all'", field="group_id"
        ) from None

    api_send(f"{cbrain_url}/groups/switch?id={group_id}", api_token)
    group_data = api_get(f"{cbrain_url}/groups/{group_id}", api_token)

    credentials = load_credentials()
    if credentials is not None:
        credentials["current_group_id"] = group_id
        credentials["current_group_name"] = group_data.get("name", "Unknown")
        save_credentials(credentials)

    return group_data


def unswitch_project(args):
    """
    Clear the current project/group on the server and in local credentials.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    dict
        Previous and current group identifiers (all None when no project was set)
    """
    credentials = load_credentials()
    previous_group_id = None
    previous_group_name = None

    if credentials is not None:
        previous_group_id = credentials.get("current_group_id")
        previous_group_name = credentials.get("current_group_name")

    if previous_group_id:
        api_send(f"{cbrain_url}/groups/switch", api_token)

    if credentials is not None:
        credentials.pop("current_group_id", None)
        credentials.pop("current_group_name", None)
        save_credentials(credentials)

    return {
        "previous_group_id": previous_group_id,
        "previous_group_name": previous_group_name,
        "current_group_id": None,
        "current_group_name": None,
    }


def show_project(args):
    """
    Get the current project/group from credentials or show a specific project by ID.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, may include project_id

    Returns
    -------
    dict or None
        Dictionary containing project details if successful, None if no project set
    """
    # Check if a specific project ID was provided
    project_id = getattr(args, "project_id", None)

    if project_id:
        # Show specific project by ID
        try:
            return api_get(f"{cbrain_url}/groups/{project_id}", api_token)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise CliApiError(f"Project with ID {project_id} not found") from None
            raise

    credentials = load_credentials()
    if credentials is None:
        return None

    current_group_id = credentials.get("current_group_id")
    if not current_group_id:
        return None

    try:
        return api_get(f"{cbrain_url}/groups/{current_group_id}", api_token)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            credentials.pop("current_group_id", None)
            credentials.pop("current_group_name", None)
            save_credentials(credentials)
            raise CliApiError(f"Current project (ID {current_group_id}) no longer exists") from None
        raise


def list_projects(args):
    """
    Get list of all projects/groups from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag

    Returns
    -------
    list
        List of project dictionaries
    """
    return api_get(f"{cbrain_url}/groups", api_token)
