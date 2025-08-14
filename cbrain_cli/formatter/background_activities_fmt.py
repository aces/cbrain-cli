from cbrain_cli.cli_utils import json_printer, jsonl_printer, dynamic_table_print 

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

    if not activities_data:
        print("No background activities found.")
        return

    # Prepare data with formatted timestamps and items for better display
    formatted_activities = []
    for activity in activities_data:
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
        
        formatted_activity = {
            "id": activity.get("id", ""),
            "user_id": activity.get("user_id", ""),
            "remote_resource_id": activity.get("remote_resource_id", ""),
            "status": activity.get("status", ""),
            "created_at": created_at,
            "items": items_str,
            "num_successes": activity.get("num_successes", 0),
            "num_failures": activity.get("num_failures", 0)
        }
        formatted_activities.append(formatted_activity)
    
    dynamic_table_print(formatted_activities, 
                       ["id", "user_id", "remote_resource_id", "status", "created_at", "items", "num_successes", "num_failures"],
                       ["ID", "User ID", "Resource ID", "Status", "Created At", "Items", "Successes", "Failures"])

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

    print("BACKGROUND ACTIVITY DETAILS")
    print("-" * 30)

    basic_info = [
        {"field": "ID", "value": str(activity_data.get('id', 'N/A'))},
        {"field": "Type", "value": str(activity_data.get('type', 'N/A'))},
        {"field": "User ID", "value": str(activity_data.get('user_id', 'N/A'))},
        {"field": "Remote Resource ID", "value": str(activity_data.get('remote_resource_id', 'N/A'))},
        {"field": "Status", "value": str(activity_data.get('status', 'N/A'))}
    ]
    
    dynamic_table_print(basic_info, ["field", "value"], ["Field", "Value"])
    print()
    
    print("EXECUTION INFO")
    print("-" * 30)
    
    execution_info = [
        {"field": "Handler Lock", "value": str(activity_data.get('handler_lock', 'N/A'))},
        {"field": "Items", "value": str(activity_data.get('items', []))},
        {"field": "Current Item", "value": str(activity_data.get('current_item', 'N/A'))},
        {"field": "Number of Successes", "value": str(activity_data.get('num_successes', 'N/A'))},
        {"field": "Number of Failures", "value": str(activity_data.get('num_failures', 'N/A'))},
        {"field": "Messages", "value": str(activity_data.get('messages', []))},
        {"field": "Options", "value": str(activity_data.get('options', {}))}
    ]
    
    dynamic_table_print(execution_info, ["field", "value"], ["Field", "Value"])
    print()
    
    print("SCHEDULING INFO")
    print("-" * 30)
    
    scheduling_info = [
        {"field": "Created At", "value": str(activity_data.get('created_at', 'N/A'))},
        {"field": "Updated At", "value": str(activity_data.get('updated_at', 'N/A'))},
        {"field": "Start At", "value": str(activity_data.get('start_at', 'N/A'))},
        {"field": "Repeat", "value": str(activity_data.get('repeat', 'N/A'))},
        {"field": "Retry Count", "value": str(activity_data.get('retry_count', 'N/A'))},
        {"field": "Retry Delay", "value": str(activity_data.get('retry_delay', 'N/A'))}
    ]
    
    dynamic_table_print(scheduling_info, ["field", "value"], ["Field", "Value"])
