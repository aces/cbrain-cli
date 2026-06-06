from cbrain_cli.cli_utils import display_key_value_table, dynamic_table_print, output_json


def print_activities_list(activities_data, args):
    """
    Print table of background activities.

    Parameters
    ----------
    activities_data : list
        List of background activity dictionaries
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if output_json(args, activities_data):
        return

    if activities_data is None:
        return

    if not activities_data:
        print("No background activities found.")
        return

    formatted_activities = [
        {
            "id": a.get("id", ""),
            "user_id": a.get("user_id", ""),
            "remote_resource_id": a.get("remote_resource_id", ""),
            "status": a.get("status", ""),
            "created_at": (
                a.get("created_at", "").split("T")[0]
                + " "
                + a.get("created_at", "").split("T")[1].split(".")[0]
                if a.get("created_at")
                else ""
            ),
            "items": ",".join(map(str, a.get("items", []))) if a.get("items") else "",
            "num_successes": a.get("num_successes", 0),
            "num_failures": a.get("num_failures", 0),
        }
        for a in activities_data
    ]

    dynamic_table_print(
        formatted_activities,
        [
            "id",
            "user_id",
            "remote_resource_id",
            "status",
            "created_at",
            "items",
            "num_successes",
            "num_failures",
        ],
        ["ID", "User ID", "Resource ID", "Status", "Created At", "Items", "Successes", "Failures"],
    )


def print_activity_details(activity_data, args):
    """
    Print detailed information about a specific background activity.

    Parameters
    ----------
    activity_data : dict
        Dictionary containing background activity details
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if output_json(args, activity_data):
        return

    print("BACKGROUND ACTIVITY DETAILS")
    print("-" * 30)
    display_key_value_table(
        [
            ("ID", str(activity_data.get("id", "N/A"))),
            ("Type", str(activity_data.get("type", "N/A"))),
            ("User ID", str(activity_data.get("user_id", "N/A"))),
            ("Remote Resource ID", str(activity_data.get("remote_resource_id", "N/A"))),
            ("Status", str(activity_data.get("status", "N/A"))),
        ]
    )
    print()

    print("EXECUTION INFO")
    print("-" * 30)
    display_key_value_table(
        [
            ("Handler Lock", str(activity_data.get("handler_lock", "N/A"))),
            ("Items", str(activity_data.get("items", []))),
            ("Current Item", str(activity_data.get("current_item", "N/A"))),
            ("Number of Successes", str(activity_data.get("num_successes", "N/A"))),
            ("Number of Failures", str(activity_data.get("num_failures", "N/A"))),
            ("Messages", str(activity_data.get("messages", []))),
            ("Options", str(activity_data.get("options", {}))),
        ]
    )
    print()

    print("SCHEDULING INFO")
    print("-" * 30)
    display_key_value_table(
        [
            ("Created At", str(activity_data.get("created_at", "N/A"))),
            ("Updated At", str(activity_data.get("updated_at", "N/A"))),
            ("Start At", str(activity_data.get("start_at", "N/A"))),
            ("Repeat", str(activity_data.get("repeat", "N/A"))),
            ("Retry Count", str(activity_data.get("retry_count", "N/A"))),
            ("Retry Delay", str(activity_data.get("retry_delay", "N/A"))),
        ]
    )
