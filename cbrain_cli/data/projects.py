import json
import urllib.error

from cbrain_cli.cli_utils import (
    CliApiError,
    CliValidationError,
    api_get,
    api_send,
    api_token,
    cbrain_url,
)
from cbrain_cli.config import CREDENTIALS_FILE


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
        )

    api_send(f"{cbrain_url}/groups/switch?id={group_id}", api_token)
    group_data = api_get(f"{cbrain_url}/groups/{group_id}", api_token)

    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE) as f:
            credentials = json.load(f)

        credentials["current_group_id"] = group_id
        credentials["current_group_name"] = group_data.get("name", "Unknown")

        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(credentials, f, indent=2)

    return group_data


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
                raise CliApiError(f"Project with ID {project_id} not found")
            raise

    with open(CREDENTIALS_FILE) as f:
        credentials = json.load(f)

    current_group_id = credentials.get("current_group_id")
    if not current_group_id:
        return None

    try:
        return api_get(f"{cbrain_url}/groups/{current_group_id}", api_token)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            credentials.pop("current_group_id", None)
            credentials.pop("current_group_name", None)
            with open(CREDENTIALS_FILE, "w") as f:
                json.dump(credentials, f, indent=2)
            raise CliApiError(
                f"Current project (ID {current_group_id}) no longer exists"
            )
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
