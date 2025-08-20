import json
import urllib.error
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url, pagination
from cbrain_cli.config import auth_headers
from cbrain_cli.formatter.tags_fmt import print_interactive_prompts


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
    query_params = {}
    query_params = pagination(args, query_params)

    tags_endpoint = f"{cbrain_url}/tags"
    query_string = urllib.parse.urlencode(query_params)
    tags_endpoint = f"{tags_endpoint}?{query_string}"
    headers = auth_headers(api_token)

    request = urllib.request.Request(tags_endpoint, data=None, headers=headers, method="GET")

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        tags_data = json.loads(data)

    return tags_data


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
        print("Error: Tag ID is required")
        return None

    tag_endpoint = f"{cbrain_url}/tags/{tag_id}"
    headers = auth_headers(api_token)

    request = urllib.request.Request(tag_endpoint, data=None, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            tag_data = json.loads(data)
            return tag_data

    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: Tag with ID {tag_id} not found")
        else:
            print(f"Error: HTTP {e.code} - {e.reason}")
        return None


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
    # Check if interactive mode is enabled
    interactive = getattr(args, "interactive", False)

    # Get tag details
    if interactive:
        inputs = print_interactive_prompts("create")
        if not inputs:
            return None, False, None, None
        tag_name = inputs["tag_name"]
        user_id = inputs["user_id"]
        group_id = inputs["group_id"]
    else:
        tag_name = getattr(args, "name", None)
        user_id = getattr(args, "user_id", None)
        group_id = getattr(args, "group_id", None)

        if not tag_name:
            print("Error: Tag name is required. Use --name flag or -i for interactive mode")
            return None, False, None, None

        if not user_id:
            print("Error: User ID is required. Use --user-id flag or -i for interactive mode")
            return None, False, None, None

        if not group_id:
            print("Error: Group ID is required. Use --group-id flag or -i for interactive mode")
            return None, False, None, None

    # Prepare the API request
    tags_endpoint = f"{cbrain_url}/tags"
    headers = auth_headers(api_token)
    headers["Content-Type"] = "application/json"

    # Prepare the payload
    payload = {"tag": {"name": tag_name, "user_id": user_id, "group_id": group_id}}
    json_data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(tags_endpoint, data=json_data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            response_data = json.loads(data)
            return response_data, True, None, response.status

    except urllib.error.HTTPError as e:
        try:
            error_data = e.read().decode("utf-8")
            error_response = json.loads(error_data)
            error_msg = error_response.get("notice", error_data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            error_msg = e.read().decode("utf-8", errors="ignore")
        return None, False, error_msg, e.code


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
    # Check if interactive mode is enabled
    interactive = getattr(args, "interactive", False)

    # Get tag ID and details
    if interactive:
        inputs = print_interactive_prompts("update")
        if not inputs:
            return None, False, None, None
        tag_id = inputs["tag_id"]
        tag_name = inputs["tag_name"]
        user_id = inputs["user_id"]
        group_id = inputs["group_id"]
    else:
        tag_id = getattr(args, "tag_id", None)
        if not tag_id:
            print(
                "Error: Tag ID is required. Use -i flag for interactive mode "
                "or provide tag_id argument"
            )
            return None, False, None, None

        tag_name = getattr(args, "name", None)
        user_id = getattr(args, "user_id", None)
        group_id = getattr(args, "group_id", None)

        if not tag_name:
            print("Error: Tag name is required. Use --name flag or -i for interactive mode")
            return None, False, None, None

        if not user_id:
            print("Error: User ID is required. Use --user-id flag or -i for interactive mode")
            return None, False, None, None

        if not group_id:
            print("Error: Group ID is required. Use --group-id flag or -i for interactive mode")
            return None, False, None, None

    # Prepare the API request
    tag_endpoint = f"{cbrain_url}/tags/{tag_id}"
    headers = auth_headers(api_token)
    headers["Content-Type"] = "application/json"

    # Prepare the payload
    payload = {"tag": {"name": tag_name, "user_id": user_id, "group_id": group_id}}
    json_data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(tag_endpoint, data=json_data, headers=headers, method="PUT")

    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            response_data = json.loads(data)
            return response_data, True, None, response.status

    except urllib.error.HTTPError as e:
        try:
            error_data = e.read().decode("utf-8")
            error_response = json.loads(error_data)
            if e.code == 404:
                error_msg = f"Error: Tag with ID {tag_id} not found"
            else:
                error_msg = error_response.get("notice", error_data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            error_msg = e.read().decode("utf-8", errors="ignore")
        return None, False, error_msg, e.code


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
    # Check if interactive mode is enabled
    interactive = getattr(args, "interactive", False)

    # Get tag ID
    if interactive:
        inputs = print_interactive_prompts("delete")
        if not inputs:
            return False, None, None
        tag_id = inputs["tag_id"]
    else:
        tag_id = getattr(args, "tag_id", None)
        if not tag_id:
            print(
                "Error: Tag ID is required. Use -i flag for interactive mode "
                "or provide tag_id argument"
            )
            return False, None, None

    # Prepare the API request
    tag_endpoint = f"{cbrain_url}/tags/{tag_id}"
    headers = auth_headers(api_token)

    request = urllib.request.Request(tag_endpoint, data=None, headers=headers, method="DELETE")

    try:
        with urllib.request.urlopen(request) as response:
            return True, None, response.status

    except urllib.error.HTTPError as e:
        if e.code == 404:
            error_msg = f"Error: Tag with ID {tag_id} not found"
        else:
            error_msg = f"Tag deletion failed with status: {e.code}"
        return False, error_msg, e.code
