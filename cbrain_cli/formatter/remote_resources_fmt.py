from cbrain_cli.cli_utils import json_printer, jsonl_printer, dynamic_table_print

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
    if getattr(args, "json", False):
        json_printer(resources_data)
        return
    elif getattr(args, "jsonl", False):
        jsonl_printer(resources_data)
        return

    if not resources_data:
        print("No remote resources found.")
        return

    print("REMOTE RESOURCES (EXECUTION SERVERS)")
    print("-" * 80)
    
    # Prepare data with formatted boolean values for better display
    formatted_resources = []
    for resource in resources_data:
        formatted_resource = {
            "id": resource.get("id", ""),
            "name": resource.get("name", ""),
            "user_id": resource.get("user_id", ""),
            "group_id": resource.get("group_id", ""),
            "online": "Yes" if resource.get("online", False) else "No",
            "read_only": "Yes" if resource.get("read_only", False) else "No"
        }
        formatted_resources.append(formatted_resource)
    
    dynamic_table_print(formatted_resources, 
                       ["id", "name", "user_id", "group_id", "online", "read_only"],
                       ["ID", "Name", "User", "Group", "Online", "Read-Only"])
    
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
    if getattr(args, "json", False):
        json_printer(resource_data)
        return
    elif getattr(args, "jsonl", False):
        jsonl_printer(resource_data)
        return

    print("REMOTE RESOURCE DETAILS")
    print("-" * 30)
    
    # Prepare basic details as key-value pairs for table display
    basic_details = [
        {"field": "ID", "value": str(resource_data.get('id', 'N/A'))},
        {"field": "Name", "value": str(resource_data.get('name', 'N/A'))},
        {"field": "Type", "value": str(resource_data.get('type', 'N/A'))}
    ]
    
    dynamic_table_print(basic_details, ["field", "value"], ["Field", "Value"])
    print()

    print("OWNERSHIP & ACCESS")
    print("-" * 30)
    
    # Prepare ownership details as key-value pairs for table display
    ownership_details = [
        {"field": "User ID", "value": str(resource_data.get('user_id', 'N/A'))},
        {"field": "Group ID", "value": str(resource_data.get('group_id', 'N/A'))},
        {"field": "Online", "value": str(resource_data.get('online', 'N/A'))},
        {"field": "Read Only", "value": str(resource_data.get('read_only', 'N/A'))}
    ]
    
    dynamic_table_print(ownership_details, ["field", "value"], ["Field", "Value"])
    print() 