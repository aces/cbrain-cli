from cbrain_cli.cli_utils import CbrainClient, CliValidationError


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
    return CbrainClient.from_credentials().get("/bourreaux")


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
        raise CliValidationError("Remote resource ID is required", field="remote_resource")
    return CbrainClient.from_credentials().get(f"/bourreaux/{resource_id}")
