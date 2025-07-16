import json
import urllib.error
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url
from cbrain_cli.config import auth_headers


def show_data_provider(args):
    """
    Show data provider details for the specified data provider ID,
    or list all data providers if no ID is provided.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the id argument

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """

    # Get the data provider ID from the --id argument.
    data_provider_id = getattr(args, "id", None)

    if data_provider_id:
        # Show specific data provider by ID
        # Prepare the API request.
        data_provider_endpoint = f"{cbrain_url}/data_providers/{data_provider_id}"
        headers = auth_headers(api_token)

        request = urllib.request.Request(
            data_provider_endpoint, data=None, headers=headers, method="GET"
        )

        # Make the request.
        try:
            with urllib.request.urlopen(request) as response:
                data = response.read().decode("utf-8")
                provider_data = json.loads(data)

            if provider_data.get("error"):
                print(f"Error: {provider_data.get('error')}")
                return 1

            # Output the data provider details.
            print(
                f"id: {provider_data.get('id', 'N/A')}\n"
                f"name: {provider_data.get('name', 'N/A')}\n"
                f"type: {provider_data.get('type', 'N/A')}\n"
                f"remote_user: {provider_data.get('remote_user', 'N/A')}\n"
                f"remote_host: {provider_data.get('remote_host', 'N/A')}\n"
                f"remote_dir: {provider_data.get('remote_dir', 'N/A')}\n"
                f"remote_port: {provider_data.get('remote_port', 'N/A')}\n"
                f"user_id: {provider_data.get('user_id', 'N/A')}\n"
                f"group_id: {provider_data.get('group_id', 'N/A')}\n"
                f"online: {provider_data.get('online', 'N/A')}\n"
                f"read_only: {provider_data.get('read_only', 'N/A')}\n"
                f"is_browsable: {provider_data.get('is_browsable', 'N/A')}\n"
                f"is_fast_syncing: {provider_data.get('is_fast_syncing', 'N/A')}\n"
                f"allow_file_owner_change: {provider_data.get('allow_file_owner_change', 'N/A')}\n"
                f"content_storage_shared_between_users: {provider_data.get('content_storage_shared_between_users', 'N/A')}\n"
                f"description: {provider_data.get('description', 'N/A')}\n"
            )

            return 0

        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"Error: Data provider with ID {data_provider_id} not found")
            else:
                print(f"Error: HTTP {e.code} - {e.reason}")
            return 1
    else:
        # Show all data providers (same as list_data_providers but in show format)
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

        # Output all data providers in detailed format.
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

        return 0


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

def is_alive(args):
    """
    Check if a data provider is alive.
    """
    is_alive_endpoint = f"{cbrain_url}/data_providers/{args.id}/is_alive"
    headers = auth_headers(api_token)

    request = urllib.request.Request(
        is_alive_endpoint, data=None, headers=headers, method="GET"
    )

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        is_alive_data = json.loads(data)
    print(is_alive_data)


def delete_unregistered_files(args):
    """
    Delete unregistered files from a data provider.
    """

    delete_unregistered_files_endpoint = f"{cbrain_url}/data_providers/{args.id}/delete"
    headers = auth_headers(api_token)

    request = urllib.request.Request(
        delete_unregistered_files_endpoint, data=None, headers=headers, method="POST"
    )

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        delete_unregistered_files_data = json.loads(data)
    print(delete_unregistered_files_data)
