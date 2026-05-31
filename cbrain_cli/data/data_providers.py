from cbrain_cli.cli_utils import api_get, api_send, api_token, cbrain_url, pagination


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
    data = api_get(f"{cbrain_url}/data_providers/{data_provider_id}", api_token)
    if data.get("error"):
        print(f"Error: {data.get('error')}")
        return None
    return data


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
    params = pagination(args, {})
    if params is None:
        return None
    return api_get(f"{cbrain_url}/data_providers", api_token, params)


def is_alive(args):
    """
    Check if a data provider is alive.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the id argument
    """
    return api_get(f"{cbrain_url}/data_providers/{args.id}/is_alive", api_token)


def delete_unregistered_files(args):
    """
    Delete unregistered files from a data provider.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the id argument
    """
    data, _ = api_send(f"{cbrain_url}/data_providers/{args.id}/delete", api_token)
    return data
