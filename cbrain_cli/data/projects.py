import json
import urllib.error
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url
from cbrain_cli.config import CREDENTIALS_FILE, auth_headers


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
        print("Error: Group ID is required")
        return None

    # Step 1: Call the switch API
    switch_endpoint = f"{cbrain_url}/groups/switch?id={group_id}"
    headers = auth_headers(api_token)

    # Create the request
    request = urllib.request.Request(switch_endpoint, data=None, headers=headers, method="POST")

    # Make the switch request
    try:
        with urllib.request.urlopen(request) as response:
            if response.status == 200:
                # Step 2: Get group details
                group_endpoint = f"{cbrain_url}/groups/{group_id}"
                group_request = urllib.request.Request(
                    group_endpoint, data=None, headers=headers, method="GET"
                )

                with urllib.request.urlopen(group_request) as group_response:
                    group_data_text = group_response.read().decode("utf-8")
                    group_data = json.loads(group_data_text)

                # Step 3: Update credentials file with current group_id
                if CREDENTIALS_FILE.exists():
                    with open(CREDENTIALS_FILE) as f:
                        credentials = json.load(f)

                    credentials["current_group_id"] = group_id
                    credentials["current_group_name"] = group_data.get("name", "Unknown")

                    with open(CREDENTIALS_FILE, "w") as f:
                        json.dump(credentials, f, indent=2)

                return group_data
            else:
                print(f"Project switch failed with status: {response.status}")
                return None

    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: Project with ID {group_id} not found")
        elif e.code == 403:
            print(f"Error: Access denied to project {group_id}")
        else:
            print(f"Project switch failed with status: {e.code}")
        return None
    except Exception as e:
        print(f"Error switching project: {str(e)}")
        return None


def show_project(args):
    """
    Get the current project/group from credentials.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    dict or None
        Dictionary containing project details if successful, None if no project set
    """
    with open(CREDENTIALS_FILE) as f:
        credentials = json.load(f)

    current_group_id = credentials.get("current_group_id")
    if not current_group_id:
        return None

    # Get fresh group details from server
    group_endpoint = f"{cbrain_url}/groups/{current_group_id}"
    headers = auth_headers(api_token)

    request = urllib.request.Request(group_endpoint, data=None, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            group_data = json.loads(data)
            return group_data

    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: Current project (ID {current_group_id}) no longer exists")
            # Clear the invalid group_id from credentials
            credentials.pop("current_group_id", None)
            credentials.pop("current_group_name", None)
            with open(CREDENTIALS_FILE, "w") as f:
                json.dump(credentials, f, indent=2)
        else:
            print(f"Error getting project details: HTTP {e.code}")
        return None
    except Exception as e:
        print(f"Error getting project details: {str(e)}")
        return None


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
    # Prepare the API request.
    groups_endpoint = f"{cbrain_url}/groups"
    headers = auth_headers(api_token)

    # Create the request.
    request = urllib.request.Request(groups_endpoint, data=None, headers=headers, method="GET")

    # Make the request.
    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        projects_data = json.loads(data)

    return projects_data
