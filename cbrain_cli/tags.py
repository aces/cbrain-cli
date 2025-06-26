import json
import urllib.error
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url
from cbrain_cli.config import auth_headers


def show_tag(args):
    """
    Show tag details for the specified tag ID,
    or list all tags if no ID is provided.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the optional id argument

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """

    # Check if a specific tag ID was provided
    tag_id = getattr(args, "id", None)

    if tag_id:
        # Show specific tag details
        tags_endpoint = f"{cbrain_url}/tags/{tag_id}"
        headers = auth_headers(api_token)

        # Create the request
        request = urllib.request.Request(
            tags_endpoint, data=None, headers=headers, method="GET"
        )

        # Make the request
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            tag_data = json.loads(data)

        # Output the tag details
        print(f"id: {tag_data.get('id', 'N/A')}")
        print(f"name: {tag_data.get('name', 'N/A')}")
        print(f"user_id: {tag_data.get('user_id', 'N/A')}")
        print(f"group_id: {tag_data.get('group_id', 'N/A')}")

    else:
        # List all tags
        tags_endpoint = f"{cbrain_url}/tags"
        headers = auth_headers(api_token)

        # Create the request
        request = urllib.request.Request(
            tags_endpoint, data=None, headers=headers, method="GET"
        )

        # Make the request
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            tags_data = json.loads(data)

        # Output the tags in table format
        print("ID   Name                     User ID  Group ID")
        print("---- ------------------------ -------- --------")
        for tag in tags_data:
            tag_id = tag.get("id", "")
            tag_name = tag.get("name", "")
            user_id = tag.get("user_id", "")
            group_id = tag.get("group_id", "")
            print(f"{tag_id:<4} {tag_name:<24} {user_id:<8} {group_id}")

    return 0


def create_tag(args):
    """
    Create a new tag in CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including name, user_id, and group_id

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """

    # Prepare the API request
    tags_endpoint = f"{cbrain_url}/tags"
    headers = auth_headers(api_token)
    headers["Content-Type"] = "application/json"

    # Prepare the payload
    payload = {
        "tag": {"name": args.name, "user_id": args.user_id, "group_id": args.group_id}
    }

    # Convert payload to JSON
    json_data = json.dumps(payload).encode("utf-8")

    # Create the request
    request = urllib.request.Request(
        tags_endpoint, data=json_data, headers=headers, method="POST"
    )

    # Make the request
    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            tag_data = json.loads(data)

            if response.status == 200 or response.status == 201:
                print(
                    "Tag created successfully!\n"
                    f"id: {tag_data.get('id', 'N/A')}\n"
                    f"name: {tag_data.get('name', 'N/A')}\n"
                    f"user_id: {tag_data.get('user_id', 'N/A')}\n"
                    f"group_id: {tag_data.get('group_id', 'N/A')}\n"
                )

                return 0
            else:
                print(f"Tag creation failed with status: {response.status}")
                return 1

    except urllib.error.HTTPError as e:
        try:
            error_data = e.read().decode("utf-8")
            error_response = json.loads(error_data)
            print(f"Tag creation failed with status: {e.code}")
            if error_response.get("notice"):
                print(f"Error: {error_response['notice']}")
            else:
                print(f"Response: {error_data}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"Tag creation failed with status: {e.code}")
            print(f"Response: {e.read().decode('utf-8', errors='ignore')}")
        return 1
