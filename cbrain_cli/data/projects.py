from cbrain_cli.cli_utils import (
    CbrainClient,
    CliApiError,
    CliValidationError,
)
from cbrain_cli.config import (
    load_credentials,
    resolve_session_credentials,
    update_active_credentials,
)


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

    # Server accepts numeric id or "all" (no single project filter).
    if group_id != "all":
        try:
            group_id = int(group_id)
        except ValueError:
            raise CliValidationError(
                f"Invalid group ID '{group_id}'. Must be a number or 'all'", field="group_id"
            ) from None

    client = CbrainClient.from_credentials()
    _, switch_status = client.send("POST", f"/groups/switch?id={group_id}")
    if switch_status not in (200, 201, 204):
        raise CliApiError(f"Failed to switch project (HTTP {switch_status})")

    # "all" is session state only — no /groups/all resource.
    if group_id == "all":
        group_data = {"id": "all", "name": "all"}
    else:
        group_data = client.get(f"/groups/{group_id}")

    if load_credentials() is not None:
        update_active_credentials(
            {
                "current_group_id": group_id,
                "current_group_name": group_data.get("name", "Unknown"),
            }
        )

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
        active = resolve_session_credentials(credentials)
        previous_group_id = active.get("current_group_id")
        previous_group_name = active.get("current_group_name")

    if previous_group_id:
        CbrainClient.from_credentials().send("POST", "/groups/switch")

    if credentials is not None:
        update_active_credentials(remove_keys=["current_group_id", "current_group_name"])

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
            return CbrainClient.from_credentials().get(f"/groups/{project_id}")
        except CliApiError as e:
            if e.status == 404:
                raise CliApiError(f"Project with ID {project_id} not found") from None
            raise

    credentials = load_credentials()
    if credentials is None:
        return None

    active = resolve_session_credentials(credentials)
    current_group_id = active.get("current_group_id")
    if not current_group_id:
        return None

    # Session "all" has no Group row; mirror switch_project synthetic result.
    if current_group_id == "all":
        return {
            "id": "all",
            "name": active.get("current_group_name") or "all",
        }

    try:
        return CbrainClient.from_credentials().get(f"/groups/{current_group_id}")
    except CliApiError as e:
        if e.status == 404:
            update_active_credentials(remove_keys=["current_group_id", "current_group_name"])
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
    return CbrainClient.from_credentials().get("/groups")
