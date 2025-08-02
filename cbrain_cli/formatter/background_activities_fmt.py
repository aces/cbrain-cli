from cbrain_cli.cli_utils import json_printer, jsonl_printer 

def print_activities_list(activities_data, args):
    """
    Print list of background activities in table format.

    Parameters
    ----------
    activities_data : list
        List of background activity dictionaries
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if getattr(args, "json", False):
        json_printer(activities_data)
        return
    elif getattr(args, "jsonl", False):
        jsonl_printer(activities_data)
        return

    print(
        "ID   User ID  Resource ID  Status       Created At           Items    Successes  Failures"
    )
    print(
        "---- -------- ------------ ------------ -------------------- -------- ---------- --------"
    )
    for activity in activities_data:
        activity_id = activity.get("id", "")
        user_id = activity.get("user_id", "")
        resource_id = activity.get("remote_resource_id", "")
        status = activity.get("status", "")
        created_at = activity.get("created_at", "")
        # Format created_at to show only date and time without timezone
        if created_at:
            created_at = (
                created_at.split("T")[0]
                + " "
                + created_at.split("T")[1].split(".")[0]
            )
        items = activity.get("items", [])
        items_str = ",".join(map(str, items)) if items else ""
        num_successes = activity.get("num_successes", 0)
        num_failures = activity.get("num_failures", 0)
        print(
            f"{activity_id:<4} {user_id:<8} {resource_id:<12} {status:<12} {created_at:<20} {items_str:<8} {num_successes:<10} {num_failures}"
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
    if getattr(args, "json", False):
        json_printer(activity_data)
        return
    elif getattr(args, "jsonl", False):
        jsonl_printer(activity_data)
        return

    print(
        f"id: {activity_data.get('id', 'N/A')}\n"
        f"type: {activity_data.get('type', 'N/A')}\n"
        f"user_id: {activity_data.get('user_id', 'N/A')}\n"
        f"remote_resource_id: {activity_data.get('remote_resource_id', 'N/A')}\n"
        f"status: {activity_data.get('status', 'N/A')}\n"
        f"handler_lock: {activity_data.get('handler_lock', 'N/A')}\n"
        f"items: {activity_data.get('items', [])}\n"
        f"current_item: {activity_data.get('current_item', 'N/A')}\n"
        f"num_successes: {activity_data.get('num_successes', 'N/A')}\n"
        f"num_failures: {activity_data.get('num_failures', 'N/A')}\n"
        f"messages: {activity_data.get('messages', [])}\n"
        f"options: {activity_data.get('options', {})}\n"
        f"created_at: {activity_data.get('created_at', 'N/A')}\n"
        f"updated_at: {activity_data.get('updated_at', 'N/A')}\n"
        f"start_at: {activity_data.get('start_at', 'N/A')}\n"
        f"repeat: {activity_data.get('repeat', 'N/A')}\n"
        f"retry_count: {activity_data.get('retry_count', 'N/A')}\n"
        f"retry_delay: {activity_data.get('retry_delay', 'N/A')}\n"
    )
