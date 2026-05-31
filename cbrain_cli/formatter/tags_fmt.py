from cbrain_cli.cli_utils import dynamic_table_print, display_key_value_table, output_json


def print_tags_list(tags_data, args):
    """
    Print table of tags.

    Parameters
    ----------
    tags_data : list
        List of tag dictionaries
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if output_json(args, tags_data):
        return

    if not tags_data:
        print("No tags found.")
        return

    print("TAGS")
    print("-" * 40)
    dynamic_table_print(
        tags_data, ["id", "name", "user_id", "group_id"], ["ID", "Name", "User", "Group"]
    )
    print("-" * 40)
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
    if output_json(args, tag_data):
        return

    print("TAG DETAILS")
    print("-" * 30)
    display_key_value_table(
        [
            ("ID", str(tag_data.get("id", "N/A"))),
            ("Name", str(tag_data.get("name", "N/A"))),
            ("User ID", str(tag_data.get("user_id", "N/A"))),
            ("Group ID", str(tag_data.get("group_id", "N/A"))),
        ]
    )


def print_tag_operation_result(
    operation, tag_id=None, success=True, error_msg=None, response_status=None
):
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
            print("Tag created successfully!")
        elif operation == "update":
            print(f"Tag {tag_id} updated successfully!")
        elif operation == "delete":
            print(f"Tag {tag_id} deleted successfully!")
    else:
        if error_msg:
            print(error_msg)
        else:
            print(f"Tag {operation} failed with status: {response_status}")
