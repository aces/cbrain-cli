import json
import urllib.error
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url
from cbrain_cli.config import auth_headers


def list_remote_resources(args):
    """
    Get list of all remote resources (bourreaux/execution servers) from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag

    Returns
    -------
    list
        List of remote resource dictionaries
    """
    bourreaux_endpoint = f"{cbrain_url}/bourreaux"
    headers = auth_headers(api_token)

    request = urllib.request.Request(bourreaux_endpoint, data=None, headers=headers, method="GET")

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        bourreaux_data = json.loads(data)

    return bourreaux_data


def show_remote_resource(args):
    """
    Get detailed information about a specific remote resource from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the remote_resource argument with resource_id

    Returns
    -------
    dict or None
        Dictionary containing remote resource details if successful, None otherwise
    """
    # Get the remote resource ID from the remote_resource argument
    resource_id = getattr(args, "remote_resource", None)
    if not resource_id:
        print("Error: Remote resource ID is required")
        return None

    bourreau_endpoint = f"{cbrain_url}/bourreaux/{resource_id}"
    headers = auth_headers(api_token)

    request = urllib.request.Request(bourreau_endpoint, data=None, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            bourreau_data = json.loads(data)
            return bourreau_data

    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: Remote resource with ID {resource_id} not found")
        else:
            print(f"Error: HTTP {e.code} - {e.reason}")
        return None
