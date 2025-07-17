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
        Command line arguments, including the --json flag, filter options, and pagination

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    # Validate per_page parameter
    per_page = getattr(args, "per_page", 25)
    if per_page < 5 or per_page > 1000:
        print("Error: per-page must be between 5 and 1000")
        return 1

    # Build query parameters for filtering
    query_params = {}

    # Add filter parameters if provided
    if hasattr(args, "group_id") and args.group_id is not None:
        query_params["group_id"] = str(args.group_id)

    if hasattr(args, "dp_id") and args.dp_id is not None:
        query_params["data_provider_id"] = str(args.dp_id)

    if hasattr(args, "user_id") and args.user_id is not None:
        query_params["user_id"] = str(args.user_id)

    if hasattr(args, "parent_id") and args.parent_id is not None:
        query_params["parent_id"] = str(args.parent_id)

    if hasattr(args, "file_type") and args.file_type is not None:
        query_params["type"] = args.file_type

    all_files = []
    show_all = getattr(args, "all", False)
    
    if show_all:
        page = 1
        max_per_page = 1000
        
        while True:
            current_query_params = query_params.copy()
            current_query_params["page"] = str(page)
            current_query_params["per_page"] = str(max_per_page)
            
            userfiles_endpoint = f"{cbrain_url}/userfiles"
            query_string = urllib.parse.urlencode(current_query_params)
            userfiles_endpoint = f"{userfiles_endpoint}?{query_string}"
            
            headers = auth_headers(api_token)
            request = urllib.request.Request(
                userfiles_endpoint, data=None, headers=headers, method="GET"
            )

            with urllib.request.urlopen(request) as response:
                data = response.read().decode("utf-8")
                files_data = json.loads(data)
            
            if not files_data:  # Stop if no more files
                break
            
            all_files.extend(files_data)
            page += 1
        
        files_data = all_files
    else:
        page = getattr(args, "page", 1)
        if page < 1:
            print("Error: page must be 1 or greater")
            return 1
            
        query_params["page"] = str(page)
        query_params["per_page"] = str(per_page)
        
        userfiles_endpoint = f"{cbrain_url}/userfiles"
        query_string = urllib.parse.urlencode(query_params)
        userfiles_endpoint = f"{userfiles_endpoint}?{query_string}"
        
        headers = auth_headers(api_token)
        request = urllib.request.Request(
            userfiles_endpoint, data=None, headers=headers, method="GET"
        )
        
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            files_data = json.loads(data)

    ids_only = getattr(args, "ids_only", False)
    
    if getattr(args, "json", False):
        if ids_only:
            # Extract only IDs for JSON output
            id_list = [file_item.get("id") for file_item in files_data]
            print(json.dumps(id_list, indent=2))
        else:
            print(json.dumps(files_data, indent=2))
    else:
        if ids_only:
            # Show only file IDs
            print("IDs: ",end="")
            for file_item in files_data:
                file_id = file_item.get("id", "")
                print(file_id,end=", ")
        else:
            print("ID   Type        File Name")
            print("---- ----------- -----------------------")
            for file_item in files_data:
                file_id = file_item.get("id", "")
                file_type = file_item.get("type", "")
                file_name = file_item.get("name", "")
                print(f"{file_id:<4} {file_type:<11} {file_name}")
        
        if show_all:
            print(f"\nTotal files: {len(files_data)}")
        elif not ids_only:
            print(f"\nShowing page {page} ({len(files_data)} files)")

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
        print(
            "ID   User ID  Resource ID  Status       Created At           Items    Successes  Failures"
        )
        print(
            "---- -------- ------------ ------------ -------------------- -------- ---------- --------"
        )
        for activity in background_activities_data:
            activity_id = activity.get("id", "")
            user_id = activity.get("user_id", "")
            resource_id = activity.get("remote_resource_id", "")
            status = activity.get("status", "")
            created_at = activity.get("created_at", "")
            # Format created_at to show only date and time without timezone
            if created_at:
                created_at = (
                    created_at.split("T")[0]
                    + " "
                    + created_at.split("T")[1].split(".")[0]
                )
            items = activity.get("items", [])
            items_str = ",".join(map(str, items)) if items else ""
            num_successes = activity.get("num_successes", 0)
            num_failures = activity.get("num_failures", 0)
            print(
                f"{activity_id:<4} {user_id:<8} {resource_id:<12} {status:<12} {created_at:<20} {items_str:<8} {num_successes:<10} {num_failures}"
            )

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
            print(
                f"id: {activity_data.get('id', 'N/A')}\n"
                f"type: {activity_data.get('type', 'N/A')}\n"
                f"user_id: {activity_data.get('user_id', 'N/A')}\n"
                f"remote_resource_id: {activity_data.get('remote_resource_id', 'N/A')}\n"
                f"status: {activity_data.get('status', 'N/A')}\n"
                f"handler_lock: {activity_data.get('handler_lock', 'N/A')}\n"
                f"items: {activity_data.get('items', [])}\n"
                f"current_item: {activity_data.get('current_item', 'N/A')}\n"
                f"num_successes: {activity_data.get('num_successes', 'N/A')}\n"
                f"num_failures: {activity_data.get('num_failures', 'N/A')}\n"
                f"messages: {activity_data.get('messages', [])}\n"
                f"options: {activity_data.get('options', {})}\n"
                f"created_at: {activity_data.get('created_at', 'N/A')}\n"
                f"updated_at: {activity_data.get('updated_at', 'N/A')}\n"
                f"start_at: {activity_data.get('start_at', 'N/A')}\n"
                f"repeat: {activity_data.get('repeat', 'N/A')}\n"
                f"retry_count: {activity_data.get('retry_count', 'N/A')}\n"
                f"retry_delay: {activity_data.get('retry_delay', 'N/A')}\n"
            )

        return 0

    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: Background activity with ID {activity_id} not found")
        else:
            print(f"Error: HTTP {e.code} - {e.reason}")
        return 1
