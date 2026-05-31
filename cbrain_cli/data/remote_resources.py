from cbrain_cli.cli_utils import api_get, api_token, cbrain_url


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
    return api_get(f"{cbrain_url}/bourreaux", api_token)


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
    resource_id = getattr(args, "remote_resource", None)
    if not resource_id:
        print("Error: Remote resource ID is required")
        return None
    return api_get(f"{cbrain_url}/bourreaux/{resource_id}", api_token)
