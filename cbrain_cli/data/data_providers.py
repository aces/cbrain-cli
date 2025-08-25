import json
import urllib.error
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url, pagination
from cbrain_cli.config import auth_headers


def show_data_provider(args):
    """
    Get data provider details for the specified data provider ID.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the id argument

    Returns
    -------
    dict
        Data provider details
    """
    # Get the data provider ID from the --id argument.
    data_provider_id = getattr(args, "id", None)

    if not data_provider_id:
        return list_data_providers(args)

    # Show specific data provider by ID
    data_provider_endpoint = f"{cbrain_url}/data_providers/{data_provider_id}"
    headers = auth_headers(api_token)

    request = urllib.request.Request(
        data_provider_endpoint, data=None, headers=headers, method="GET"
    )

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        provider_data = json.loads(data)

    if provider_data.get("error"):
        print(f"Error: {provider_data.get('error')}")
        return None

    return provider_data


def list_data_providers(args):
    """
    Get list of all data providers from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag

    Returns
    -------
    list
        List of data provider dictionaries
    """
    query_params = {}
    query_params = pagination(args, query_params)

    data_providers_endpoint = f"{cbrain_url}/data_providers"
    query_string = urllib.parse.urlencode(query_params)
    data_providers_endpoint = f"{data_providers_endpoint}?{query_string}"
    headers = auth_headers(api_token)

    request = urllib.request.Request(
        data_providers_endpoint, data=None, headers=headers, method="GET"
    )

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        data_providers_data = json.loads(data)

    return data_providers_data


def is_alive(args):
    """
    Check if a data provider is alive.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the id argument
    """
    is_alive_endpoint = f"{cbrain_url}/data_providers/{args.id}/is_alive"
    headers = auth_headers(api_token)

    request = urllib.request.Request(is_alive_endpoint, data=None, headers=headers, method="GET")

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        is_alive_data = json.loads(data)

    return is_alive_data


def delete_unregistered_files(args):
    """
    Delete unregistered files from a data provider.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the id argument
    """
    delete_unregistered_files_endpoint = f"{cbrain_url}/data_providers/{args.id}/delete"
    headers = auth_headers(api_token)

    request = urllib.request.Request(
        delete_unregistered_files_endpoint, data=None, headers=headers, method="POST"
    )

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        delete_unregistered_files_data = json.loads(data)

    return delete_unregistered_files_data
