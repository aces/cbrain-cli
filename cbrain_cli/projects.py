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
    int
        Exit code (0 for success, 1 for failure)
    """
    # Get the group ID from the group_id argument
    group_id = getattr(args, "group_id", None)
    if not group_id:
        print("Error: Group ID is required")
        return 1

    # Step 1: Call the switch API
    switch_endpoint = f"{cbrain_url}/groups/switch?id={group_id}"
    headers = auth_headers(api_token)

    # Create the request
    request = urllib.request.Request(
        switch_endpoint, data=None, headers=headers, method="POST"
    )

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
                    with open(CREDENTIALS_FILE, "r") as f:
                        credentials = json.load(f)

                    credentials["current_group_id"] = group_id
                    credentials["current_group_name"] = group_data.get(
                        "name", "Unknown"
                    )

                    with open(CREDENTIALS_FILE, "w") as f:
                        json.dump(credentials, f, indent=2)

                # Step 4: Display success message
                group_name = group_data.get("name", "Unknown")
                print(f'Current project is now "{group_name}" ID={group_id}')

                return 0
            else:
                print(f"Project switch failed with status: {response.status}")
                return 1

    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: Project with ID {group_id} not found")
        elif e.code == 403:
            print(f"Error: Access denied to project {group_id}")
        else:
            print(f"Project switch failed with status: {e.code}")
        return 1
    except Exception as e:
        print(f"Error switching project: {str(e)}")
        return 1


def show_project(args):
    """
    Show the current project/group from credentials.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    with open(CREDENTIALS_FILE, "r") as f:
        credentials = json.load(f)

    current_group_id = credentials.get("current_group_id")
    if not current_group_id:
        print(
            "No current project set. Use 'cbrain project switch <ID>' to set a project."
        )
        return 0

    # Get fresh group details from server
    group_endpoint = f"{cbrain_url}/groups/{current_group_id}"
    headers = auth_headers(api_token)

    request = urllib.request.Request(
        group_endpoint, data=None, headers=headers, method="GET"
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            group_data = json.loads(data)

            group_name = group_data.get("name", "Unknown")
            print(f'Current project is "{group_name}" ID={current_group_id}')

            return 0

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
        return 1
    except Exception as e:
        print(f"Error getting project details: {str(e)}")
        return 1


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
