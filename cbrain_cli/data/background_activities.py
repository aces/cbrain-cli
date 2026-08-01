from cbrain_cli.cli_utils import CbrainClient, CliValidationError


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
    return CbrainClient.from_credentials().get("/background_activities")


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
        raise CliValidationError("Background activity ID is required", field="id")
    return CbrainClient.from_credentials().get(f"/background_activities/{activity_id}")
