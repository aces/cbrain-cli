import json
import urllib.parse
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url
from cbrain_cli.config import auth_headers

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
