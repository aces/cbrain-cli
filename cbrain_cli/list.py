import json
import urllib.parse
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url
from cbrain_cli.config import auth_headers


def list_projects(args):
    """
    List all projects/groups from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """

    # Prepare the API request.
    groups_endpoint = f"{cbrain_url}/groups"
    headers = auth_headers(api_token)

    # Create the request.
    request = urllib.request.Request(
        groups_endpoint, data=None, headers=headers, method="GET"
    )

    # Make the request.
    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        projects_data = json.loads(data)

    # Output in requested format.
    if getattr(args, "json", False):
        # JSON format.
        formatted_data = []
        for project in projects_data:
            formatted_data.append(
                {
                    "id": project.get("id"),
                    "type": project.get("type"),
                    "name": project.get("name"),
                }
            )
        print(json.dumps(formatted_data, indent=2))
    else:
        # Table format.
        print("ID Type        Project Name")
        print("-- ----------- ----------------")
        for project in projects_data:
            project_id = project.get("id", "")
            project_type = project.get("type", "")
            project_name = project.get("name", "")
            print(f"{project_id:<2} {project_type:<11} {project_name}")

    return


def list_files(args):
    """
    List all files from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag and filter options

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    # Build query parameters for filtering
    query_params = {}

    # Add filter parameters if provided
    if hasattr(args, "group_id") and args.group_id is not None:
        query_params["group_id"] = str(args.group_id)

    if hasattr(args, "data_provider_id") and args.data_provider_id is not None:
        query_params["data_provider_id"] = str(args.data_provider_id)

    if hasattr(args, "user_id") and args.user_id is not None:
        query_params["user_id"] = str(args.user_id)

    if hasattr(args, "parent_id") and args.parent_id is not None:
        query_params["parent_id"] = str(args.parent_id)

    if hasattr(args, "file_type") and args.file_type is not None:
        query_params["type"] = args.file_type

    # Prepare the API request.
    userfiles_endpoint = f"{cbrain_url}/userfiles"

    # Add query parameters if any filters are provided
    if query_params:
        query_string = urllib.parse.urlencode(query_params)
        userfiles_endpoint = f"{userfiles_endpoint}?{query_string}"

    headers = auth_headers(api_token)

    # Create the request.
    request = urllib.request.Request(
        userfiles_endpoint, data=None, headers=headers, method="GET"
    )

    # Make the request.
    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        files_data = json.loads(data)

    # Output in requested format.
    if getattr(args, "json", False):
        print(json.dumps(files_data, indent=2))
    else:
        # Table format.
        print("ID   Type        File Name")
        print("---- ----------- -----------------------")
        for file_item in files_data:
            file_id = file_item.get("id", "")
            file_type = file_item.get("type", "")
            file_name = file_item.get("name", "")
            print(f"{file_id:<4} {file_type:<11} {file_name}")

    return


def list_data_providers(args):
    """
    List all data providers from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    # Prepare the API request.
    data_providers_endpoint = f"{cbrain_url}/data_providers"
    headers = auth_headers(api_token)

    # Create the request.
    request = urllib.request.Request(
        data_providers_endpoint, data=None, headers=headers, method="GET"
    )

    # Make the request.
    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        data_providers_data = json.loads(data)

    # Output in requested format.
    if getattr(args, "json", False):
        print(json.dumps(data_providers_data, indent=2))
    else:
        # Table format.
        print(
            "ID   Name                 Type                            Host              Online"
        )
        print(
            "---- -------------------- ------------------------------- ----------------- ------"
        )
        for provider in data_providers_data:
            provider_id = provider.get("id", "")
            provider_name = provider.get("name", "")
            provider_type = provider.get("type", "")
            provider_host = provider.get("remote_host", "")
            provider_online = "Yes" if provider.get("online", False) else "No"
            print(
                f"{provider_id:<4} {provider_name:<20} {provider_type:<31} {provider_host:<17} {provider_online}"
            )

    return


def list_background_activitites(args):
    """
    List all background activities from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    # Prepare the API request.
    background_activities_endpoint = f"{cbrain_url}/background_activities"
    headers = auth_headers(api_token)

    # Create the request.
    request = urllib.request.Request(
        background_activities_endpoint, data=None, headers=headers, method="GET"
    )

    # Make the request.
    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        background_activities_data = json.loads(data)

    # Output in requested format.
    if getattr(args, "json", False):
        print(json.dumps(background_activities_data, indent=2))
    else:
        # Table format.
        print("ID   User ID  Resource ID  Status       Created At           Items    Successes  Failures")
        print("---- -------- ------------ ------------ -------------------- -------- ---------- --------")
        for activity in background_activities_data:
            activity_id = activity.get("id", "")
            user_id = activity.get("user_id", "")
            resource_id = activity.get("remote_resource_id", "")
            status = activity.get("status", "")
            created_at = activity.get("created_at", "")
            # Format created_at to show only date and time without timezone
            if created_at:
                created_at = created_at.split("T")[0] + " " + created_at.split("T")[1].split(".")[0]
            items_count = len(activity.get("items", []))
            num_successes = activity.get("num_successes", 0)
            num_failures = activity.get("num_failures", 0)
            print(f"{activity_id:<4} {user_id:<8} {resource_id:<12} {status:<12} {created_at:<20} {items_count:<8} {num_successes:<10} {num_failures}")

    return
def show_background_activity(args):
    """
    Show details of a specific background activity from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the id argument and optional --json flag

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    # Get the background activity ID from the --id argument
    activity_id = getattr(args, "id", None)
    
    if not activity_id:
        print("Error: Background activity ID is required")
        return 1

    # Prepare the API request.
    background_activity_endpoint = f"{cbrain_url}/background_activities/{activity_id}"
    headers = auth_headers(api_token)

    # Create the request.
    request = urllib.request.Request(
        background_activity_endpoint, data=None, headers=headers, method="GET"
    )

    try:
        # Make the request.
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            activity_data = json.loads(data)

        # Output in requested format.
        if getattr(args, "json", False):
            print(json.dumps(activity_data, indent=2))
        else:
            # Detailed format.
            print(f"id: {activity_data.get('id', 'N/A')}"
            f"type: {activity_data.get('type', 'N/A')}"
            f"user_id: {activity_data.get('user_id', 'N/A')}"
            f"remote_resource_id: {activity_data.get('remote_resource_id', 'N/A')}"
            f"status: {activity_data.get('status', 'N/A')}"
            f"handler_lock: {activity_data.get('handler_lock', 'N/A')}"
            f"items: {activity_data.get('items', [])}"
            f"current_item: {activity_data.get('current_item', 'N/A')}"
            f"num_successes: {activity_data.get('num_successes', 'N/A')}"
            f"num_failures: {activity_data.get('num_failures', 'N/A')}"
            f"messages: {activity_data.get('messages', [])}"
            f"options: {activity_data.get('options', {})}"
            f"created_at: {activity_data.get('created_at', 'N/A')}"
            f"updated_at: {activity_data.get('updated_at', 'N/A')}"
            f"start_at: {activity_data.get('start_at', 'N/A')}"
            f"repeat: {activity_data.get('repeat', 'N/A')}"
            f"retry_count: {activity_data.get('retry_count', 'N/A')}"
            f"retry_delay: {activity_data.get('retry_delay', 'N/A')}")

        return 0

    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: Background activity with ID {activity_id} not found")
        else:
            print(f"Error: HTTP {e.code} - {e.reason}")
        return 1