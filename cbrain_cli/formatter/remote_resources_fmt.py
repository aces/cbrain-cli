from cbrain_cli.cli_utils import display_key_value_table, dynamic_table_print, output_json


def print_resources_list(resources_data, args):
    """
    Print table of remote resources.

    Parameters
    ----------
    resources_data : list
        List of remote resource dictionaries
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if output_json(args, resources_data):
        return

    if resources_data is None:
        return

    if not resources_data:
        print("No remote resources found.")
        return

    print("REMOTE RESOURCES (EXECUTION SERVERS)")
    print("-" * 80)

    formatted_resources = [
        {
            "id": r.get("id", ""),
            "name": r.get("name", ""),
            "user_id": r.get("user_id", ""),
            "group_id": r.get("group_id", ""),
            "online": "Yes" if r.get("online", False) else "No",
            "read_only": "Yes" if r.get("read_only", False) else "No",
        }
        for r in resources_data
    ]

    dynamic_table_print(
        formatted_resources,
        ["id", "name", "user_id", "group_id", "online", "read_only"],
        ["ID", "Name", "User", "Group", "Online", "Read-Only"],
    )

    print("-" * 80)
    print(f"Total: {len(resources_data)} remote resource(s)")


def print_resource_details(resource_data, args):
    """
    Print detailed information about a specific remote resource.

    Parameters
    ----------
    resource_data : dict
        Dictionary containing remote resource details
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if output_json(args, resource_data):
        return

    print("REMOTE RESOURCE DETAILS")
    print("-" * 30)
    display_key_value_table(
        [
            ("ID", str(resource_data.get("id", "N/A"))),
            ("Name", str(resource_data.get("name", "N/A"))),
            ("Type", str(resource_data.get("type", "N/A"))),
        ]
    )
    print()

    print("OWNERSHIP & ACCESS")
    print("-" * 30)
    display_key_value_table(
        [
            ("User ID", str(resource_data.get("user_id", "N/A"))),
            ("Group ID", str(resource_data.get("group_id", "N/A"))),
            ("Online", str(resource_data.get("online", "N/A"))),
            ("Read Only", str(resource_data.get("read_only", "N/A"))),
        ]
    )
    print()
