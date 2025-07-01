import json
import urllib.error
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url
from cbrain_cli.config import auth_headers


def list_remote_resources(args):
    """
    List all remote resources (bourreaux/execution servers) from CBRAIN.

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
    bourreaux_endpoint = f"{cbrain_url}/bourreaux"
    headers = auth_headers(api_token)

    # Create the request.
    request = urllib.request.Request(
        bourreaux_endpoint, data=None, headers=headers, method="GET"
    )

    # Make the request.
    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        bourreaux_data = json.loads(data)

    # Output in requested format.
    if getattr(args, "json", False):
        print(json.dumps(bourreaux_data, indent=2))
    else:
        # Table format.
        if not bourreaux_data:
            print("No remote resources found.")
            return
            
        print("REMOTE RESOURCES (EXECUTION SERVERS)")
        print("-" * 80)
        print(f"{'ID':<6} {'Name':<25} {'User':<6} {'Group':<6} {'Online':<8} {'Read-Only':<10}")
        print("-" * 80)
        for bourreau in bourreaux_data:
            bourreau_id = str(bourreau.get("id", ""))
            bourreau_name = bourreau.get("name", "")
            # Truncate long names.
            if len(bourreau_name) > 24:
                bourreau_name = bourreau_name[:21] + "..."
            user_id = str(bourreau.get("user_id", ""))
            group_id = str(bourreau.get("group_id", ""))
            online = "Yes" if bourreau.get("online", False) else "No"
            read_only = "Yes" if bourreau.get("read_only", False) else "No"
            print(f"{bourreau_id:<6} {bourreau_name:<25} {user_id:<6} {group_id:<6} {online:<8} {read_only:<10}")
        print("-" * 80)
        print(f"Total: {len(bourreaux_data)} remote resource(s)")

    return 0


def show_remote_resource(args):
    """
    Show detailed information about a specific remote resource from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the remote_resource argument with resource_id

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    # Get the remote resource ID from the remote_resource argument
    resource_id = getattr(args, "remote_resource", None)
    if not resource_id:
        print("Error: Remote resource ID is required")
        return 1

    # Prepare the API request.
    bourreau_endpoint = f"{cbrain_url}/bourreaux/{resource_id}"
    headers = auth_headers(api_token)

    # Create the request.
    request = urllib.request.Request(
        bourreau_endpoint, data=None, headers=headers, method="GET"
    )

    # Make the request.
    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            bourreau_data = json.loads(data)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: Remote resource with ID {resource_id} not found")
            return 1
        else:
            print(f"Error: HTTP {e.code} - {e.reason}")
            return 1

    # Output the remote resource details.
    print("REMOTE RESOURCE DETAILS")
    print("-" * 30)
    print(f"ID:                        {bourreau_data.get('id', 'N/A')}")
    print(f"Name:                      {bourreau_data.get('name', 'N/A')}")
    print(f"Type:                      {bourreau_data.get('type', 'N/A')}")
    print()
    
    print("OWNERSHIP & ACCESS")
    print("-" * 30)
    print(f"User ID:                   {bourreau_data.get('user_id', 'N/A')}")
    print(f"Group ID:                  {bourreau_data.get('group_id', 'N/A')}")
    print(f"Online:                    {bourreau_data.get('online', 'N/A')}")
    print(f"Read Only:                 {bourreau_data.get('read_only', 'N/A')}")
    print()
    
    return 0
