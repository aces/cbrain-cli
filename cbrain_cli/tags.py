import json
import urllib.error
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url
from cbrain_cli.config import auth_headers


def list_tags(args):
    """
    List all tags from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    # Prepare the API request.
    tags_endpoint = f"{cbrain_url}/tags"
    headers = auth_headers(api_token)

    # Create the request.
    request = urllib.request.Request(
        tags_endpoint, data=None, headers=headers, method="GET"
    )

    # Make the request.
    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        tags_data = json.loads(data)

    # Output in requested format.
    if getattr(args, "json", False):
        print(json.dumps(tags_data, indent=2))
    else:
        # Table format.
        if not tags_data:
            print("No tags found.")
            return

        print("TAGS")
        print("-" * 60)
        print(f"{'ID':<6} {'Name':<25} {'User':<6} {'Group':<6}")
        print("-" * 60)
        for tag in tags_data:
            tag_id = str(tag.get("id", ""))
            tag_name = tag.get("name", "")
            # Truncate long names.
            if len(tag_name) > 24:
                tag_name = tag_name[:21] + "..."
            user_id = str(tag.get("user_id", ""))
            group_id = str(tag.get("group_id", ""))
            print(f"{tag_id:<6} {tag_name:<25} {user_id:<6} {group_id:<6}")
        print("-" * 60)
        print(f"Total: {len(tags_data)} tag(s)")

    return 0


def show_tag(args):
    """
    Show detailed information about a specific tag from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the id argument

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    # Get the tag ID from the id argument.
    tag_id = getattr(args, "id", None)
    if not tag_id:
        print("Error: Tag ID is required")
        return 1

    # Prepare the API request.
    tag_endpoint = f"{cbrain_url}/tags/{tag_id}"
    headers = auth_headers(api_token)

    # Create the request.
    request = urllib.request.Request(
        tag_endpoint, data=None, headers=headers, method="GET"
    )

    # Make the request.
    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            tag_data = json.loads(data)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: Tag with ID {tag_id} not found")
            return 1
        else:
            print(f"Error: HTTP {e.code} - {e.reason}")
            return 1

    # Output the tag details.
    print("TAG DETAILS")
    print("-" * 30)
    print(f"ID:                        {tag_data.get('id', 'N/A')}")
    print(f"Name:                      {tag_data.get('name', 'N/A')}")
    print(f"User ID:                   {tag_data.get('user_id', 'N/A')}")
    print(f"Group ID:                  {tag_data.get('group_id', 'N/A')}")

    return 0


def create_tag(args):
    """
    Create a new tag in CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """

    # Check if interactive mode is enabled
    interactive = getattr(args, "interactive", False)

    # Get tag details
    if interactive:
        tag_name = input("Enter tag name: ").strip()
        if not tag_name:
            print("Error: Tag name is required")
            return 1

        user_id_input = input("Enter user ID: ").strip()
        if not user_id_input:
            print("Error: User ID is required")
            return 1

        try:
            user_id = int(user_id_input)
        except ValueError:
            print("Error: User ID must be a number")
            return 1

        group_id_input = input("Enter group ID: ").strip()
        if not group_id_input:
            print("Error: Group ID is required")
            return 1

        try:
            group_id = int(group_id_input)
        except ValueError:
            print("Error: Group ID must be a number")
            return 1
    else:
        tag_name = getattr(args, "name", None)
        user_id = getattr(args, "user_id", None)
        group_id = getattr(args, "group_id", None)

        if not tag_name:
            print(
                "Error: Tag name is required. Use --name flag or -i for interactive mode"
            )
            return 1

        if not user_id:
            print(
                "Error: User ID is required. Use --user-id flag or -i for interactive mode"
            )
            return 1

        if not group_id:
            print(
                "Error: Group ID is required. Use --group-id flag or -i for interactive mode"
            )
            return 1

    # Prepare the API request
    tags_endpoint = f"{cbrain_url}/tags"
    headers = auth_headers(api_token)
    headers["Content-Type"] = "application/json"

    # Prepare the payload
    payload = {"tag": {"name": tag_name, "user_id": user_id, "group_id": group_id}}

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

            if response.status == 200 or response.status == 201:
                print("TAG CREATED SUCCESSFULLY!")

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


def update_tag(args):
    """
    Update an existing tag in CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """

    # Check if interactive mode is enabled
    interactive = getattr(args, "interactive", False)

    # Get tag ID to update
    tag_id = getattr(args, "tag_id", None)

    # If no tag ID provided and not in interactive mode, show error
    if not tag_id and not interactive:
        print(
            "Error: Tag ID is required. Use -i flag for interactive mode or provide tag_id argument"
        )
        return 1

    # If no tag ID provided but in interactive mode, ask for it
    if not tag_id and interactive:
        tag_id_input = input("Enter tag ID to update: ").strip()
        if not tag_id_input:
            print("Error: Tag ID is required")
            return 1

        try:
            tag_id = int(tag_id_input)
        except ValueError:
            print("Error: Tag ID must be a number")
            return 1

    # Get new tag details
    if interactive:
        print(f"\nUpdating tag {tag_id}...")
        print("Enter new values:")

        tag_name = input("Enter new tag name: ").strip()
        if not tag_name:
            print("Error: Tag name is required")
            return 1

        user_id_input = input("Enter new user ID: ").strip()
        if not user_id_input:
            print("Error: User ID is required")
            return 1

        try:
            user_id = int(user_id_input)
        except ValueError:
            print("Error: User ID must be a number")
            return 1

        group_id_input = input("Enter new group ID: ").strip()
        if not group_id_input:
            print("Error: Group ID is required")
            return 1

        try:
            group_id = int(group_id_input)
        except ValueError:
            print("Error: Group ID must be a number")
            return 1
    else:
        tag_name = getattr(args, "name", None)
        user_id = getattr(args, "user_id", None)
        group_id = getattr(args, "group_id", None)

        if not tag_name:
            print(
                "Error: Tag name is required. Use --name flag or -i for interactive mode"
            )
            return 1

        if not user_id:
            print(
                "Error: User ID is required. Use --user-id flag or -i for interactive mode"
            )
            return 1

        if not group_id:
            print(
                "Error: Group ID is required. Use --group-id flag or -i for interactive mode"
            )
            return 1

    # Prepare the API request
    tag_endpoint = f"{cbrain_url}/tags/{tag_id}"
    headers = auth_headers(api_token)
    headers["Content-Type"] = "application/json"

    # Prepare the payload
    payload = {"tag": {"name": tag_name, "user_id": user_id, "group_id": group_id}}

    # Convert payload to JSON
    json_data = json.dumps(payload).encode("utf-8")

    # Create the request
    request = urllib.request.Request(
        tag_endpoint, data=json_data, headers=headers, method="PUT"
    )

    try:
        with urllib.request.urlopen(request) as response:
            if response.status == 200 or response.status == 201:
                print(f"\nTag {tag_id} updated successfully!")

                return 0
            else:
                print(f"Tag update failed with status: {response.status}")
                return 1

    except urllib.error.HTTPError as e:
        try:
            error_data = e.read().decode("utf-8")
            error_response = json.loads(error_data)
            print(f"Tag update failed with status: {e.code}")
            if e.code == 404:
                print(f"Error: Tag with ID {tag_id} not found")
            elif error_response.get("notice"):
                print(f"Error: {error_response['notice']}")
            else:
                print(f"Response: {error_data}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"Tag update failed with status: {e.code}")
            print(f"Response: {e.read().decode('utf-8', errors='ignore')}")
        return 1


def delete_tag(args):
    """
    Delete a tag from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """

    # Check if interactive mode is enabled
    interactive = getattr(args, "interactive", False)

    # Get tag ID to delete
    tag_id = getattr(args, "tag_id", None)

    # If no tag ID provided and not in interactive mode, show error
    if not tag_id and not interactive:
        print(
            "Error: Tag ID is required. Use -i flag for interactive mode or provide tag_id argument"
        )
        return 1

    # If no tag ID provided but in interactive mode, ask for it
    if not tag_id and interactive:
        tag_id_input = input("Enter tag ID to delete: ").strip()
        if not tag_id_input:
            print("Error: Tag ID is required")
            return 1

        try:
            tag_id = int(tag_id_input)
        except ValueError:
            print("Error: Tag ID must be a number")
            return 1

    # Confirmation prompt (always ask in interactive mode, or if no tag ID was provided as argument)
    if interactive:
        confirm = (
            input(f"\nAre you sure you want to delete tag {tag_id}? (y/N): ")
            .strip()
            .lower()
        )
        if confirm not in ["y", "yes"]:
            print("Tag deletion cancelled.")
            return 0

    # Prepare the API request
    tag_endpoint = f"{cbrain_url}/tags/{tag_id}"
    headers = auth_headers(api_token)

    # Create the request
    request = urllib.request.Request(
        tag_endpoint, data=None, headers=headers, method="DELETE"
    )

    # Make the request
    try:
        with urllib.request.urlopen(request) as response:
            if response.status == 200 or response.status == 204:
                print(f"\nTag {tag_id} deleted successfully!")
                return 0
            else:
                print(f"Tag deletion failed with status: {response.status}")
                return 1

    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: Tag with ID {tag_id} not found")
        else:
            print(f"Tag deletion failed with status: {e.code}")
            print(f"Response: {e.read().decode('utf-8', errors='ignore')}")
        return 1
