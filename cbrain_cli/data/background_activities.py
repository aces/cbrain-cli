import json
import urllib.parse
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url
from cbrain_cli.config import auth_headers


def list_background_activities(args):
    """
    Get list of all background activities from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag

    Returns
    -------
    list or None
        List of background activity dictionaries if successful, None if error
    """
    background_activities_endpoint = f"{cbrain_url}/background_activities"
    headers = auth_headers(api_token)

    request = urllib.request.Request(
        background_activities_endpoint, data=None, headers=headers, method="GET"
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            background_activities_data = json.loads(data)
            return background_activities_data
    except Exception as e:
        print(f"Error fetching background activities: {str(e)}")
        return None


def show_background_activity(args):
    """
    Get detailed information about a specific background activity from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the id argument

    Returns
    -------
    dict or None
        Dictionary containing background activity details if successful, None otherwise
    """
    # Get the background activity ID from the --id argument
    activity_id = getattr(args, "id", None)
    if not activity_id:
        print("Error: Background activity ID is required")
        return None

    background_activity_endpoint = f"{cbrain_url}/background_activities/{activity_id}"
    headers = auth_headers(api_token)

    request = urllib.request.Request(
        background_activity_endpoint, data=None, headers=headers, method="GET"
    )

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        activity_data = json.loads(data)
        return activity_data
