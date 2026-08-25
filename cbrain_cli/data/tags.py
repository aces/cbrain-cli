from cbrain_cli.cli_utils import (
    CbrainClient,
    CliValidationError,
    pagination,
)

tags = [
    ("name", "Tag name", "--name"),
    ("user_id", "User ID", "--user-id"),
    ("group_id", "Group ID", "--group-id"),
]


def _tag_payload(args):
    for attr, label, flag in tags:
        if not getattr(args, attr, None):
            raise CliValidationError(f"{label} is required. Use {flag} flag", field=flag)
    return {"tag": {"name": args.name, "user_id": args.user_id, "group_id": args.group_id}}


def list_tags(args):
    """
    Get list of all tags from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag

    Returns
    -------
    list
        List of tag dictionaries
    """
    params = pagination(args, {})
    return CbrainClient.from_credentials().get("/tags", params=params)


def show_tag(args):
    """
    Get detailed information about a specific tag from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the id argument

    Returns
    -------
    dict or None
        Dictionary containing tag details if successful, None otherwise
    """
    # Get the tag ID from the id argument.
    tag_id = getattr(args, "id", None)
    if not tag_id:
        raise CliValidationError("Tag ID is required", field="id")
    return CbrainClient.from_credentials().get(f"/tags/{tag_id}")


def create_tag(args):
    """
    Create a new tag in CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    tuple
        (response_data, success, error_msg, response_status)
    """
    # Get tag details from command line arguments
    payload = _tag_payload(args)
    data, status = CbrainClient.from_credentials().send("POST", "/tags", payload=payload)
    success = status in (200, 201, 204)
    return data, success, None, status


def update_tag(args):
    """
    Update an existing tag in CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    tuple
        (response_data, success, error_msg, response_status)
    """
    # Get tag ID and details from command line arguments
    tag_id = getattr(args, "tag_id", None)
    if not tag_id:
        raise CliValidationError("Tag ID is required", field="tag_id")
    payload = _tag_payload(args)
    data, status = CbrainClient.from_credentials().send("PUT", f"/tags/{tag_id}", payload=payload)
    success = status in (200, 201, 204)
    return data, success, None, status


def delete_tag(args):
    """
    Delete a tag from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    tuple
        (success, error_msg, response_status)
    """
    # Get tag ID from command line arguments
    tag_id = getattr(args, "tag_id", None)
    if not tag_id:
        raise CliValidationError("Tag ID is required", field="tag_id")
    _, status = CbrainClient.from_credentials().send("DELETE", f"/tags/{tag_id}")
    success = status in (200, 201, 204)
    return success, None, status
