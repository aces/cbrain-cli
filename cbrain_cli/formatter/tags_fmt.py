from cbrain_cli.cli_utils import json_printer,jsonl_printer

def print_tags_list(tags_data, args):
    """
    Print list of tags in table format.

    Parameters
    ----------
    tags_data : list
        List of tag dictionaries
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if getattr(args, "json", False):
        json_printer(tags_data)
        return
    elif getattr(args, "jsonl", False):
        jsonl_printer(tags_data)
        return

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

def print_tag_details(tag_data, args):
    """
    Print detailed information about a specific tag.

    Parameters
    ----------
    tag_data : dict
        Dictionary containing tag details
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if getattr(args, "json", False):
        json_printer(tag_data)
        return
    elif getattr(args, "jsonl", False):
        jsonl_printer(tag_data)
        return

    print("TAG DETAILS")
    print("-" * 30)
    print(f"ID:                        {tag_data.get('id', 'N/A')}")
    print(f"Name:                      {tag_data.get('name', 'N/A')}")
    print(f"User ID:                   {tag_data.get('user_id', 'N/A')}")
    print(f"Group ID:                  {tag_data.get('group_id', 'N/A')}")

def print_tag_operation_result(operation, tag_id=None, success=True, error_msg=None, response_status=None):
    """
    Print result of a tag operation (create, update, delete).

    Parameters
    ----------
    operation : str
        Operation type ("create", "update", or "delete")
    tag_id : int, optional
        ID of the tag being operated on
    success : bool
        Whether the operation was successful
    error_msg : str, optional
        Error message if operation failed
    response_status : int, optional
        HTTP response status code if operation failed
    """
    if success:
        if operation == "create":
            print("TAG CREATED SUCCESSFULLY!")
        elif operation == "update":
            print(f"\nTag {tag_id} updated successfully!")
        elif operation == "delete":
            print(f"\nTag {tag_id} deleted successfully!")
    else:
        if error_msg:
            print(error_msg)
        else:
            print(f"Tag {operation} failed with status: {response_status}")

def print_interactive_prompts(operation="create"):
    """
    Print interactive prompts for tag operations.

    Parameters
    ----------
    operation : str
        Operation type ("create", "update", or "delete")

    Returns
    -------
    dict
        Dictionary containing user inputs
    """
    if operation == "delete":
        tag_id_input = input("Enter tag ID to delete: ").strip()
        if not tag_id_input:
            print("Error: Tag ID is required")
            return None
        try:
            tag_id = int(tag_id_input)
            confirm = input(f"\nAre you sure you want to delete tag {tag_id}? (y/N): ").strip().lower()
            if confirm not in ["y", "yes"]:
                print("Tag deletion cancelled.")
                return None
            return {"tag_id": tag_id}
        except ValueError:
            print("Error: Tag ID must be a number")
            return None

    if operation == "update":
        tag_id_input = input("Enter tag ID to update: ").strip()
        if not tag_id_input:
            print("Error: Tag ID is required")
            return None
        try:
            tag_id = int(tag_id_input)
            print(f"\nUpdating tag {tag_id}...")
            print("Enter new values:")
        except ValueError:
            print("Error: Tag ID must be a number")
            return None
    else:
        tag_id = None

    # Get tag details
    tag_name = input(f"Enter {'new ' if operation == 'update' else ''}tag name: ").strip()
    if not tag_name:
        print("Error: Tag name is required")
        return None

    user_id_input = input(f"Enter {'new ' if operation == 'update' else ''}user ID: ").strip()
    if not user_id_input:
        print("Error: User ID is required")
        return None

    try:
        user_id = int(user_id_input)
    except ValueError:
        print("Error: User ID must be a number")
        return None

    group_id_input = input(f"Enter {'new ' if operation == 'update' else ''}group ID: ").strip()
    if not group_id_input:
        print("Error: Group ID is required")
        return None

    try:
        group_id = int(group_id_input)
    except ValueError:
        print("Error: Group ID must be a number")
        return None

    return {
        "tag_id": tag_id,
        "tag_name": tag_name,
        "user_id": user_id,
        "group_id": group_id
    } 