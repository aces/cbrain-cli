from cbrain_cli.cli_utils import json_printer, jsonl_printer, dynamic_table_print

def print_tool_details(tool_data, args):
    """
    Print detailed information about a specific tool.

    Parameters
    ----------
    tool_data : dict
        Dictionary containing tool details
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if getattr(args, "json", False):
        json_printer(tool_data)
        return
    elif getattr(args, "jsonl", False):
        jsonl_printer(tool_data)
        return

    print("TOOL DETAILS")
    print("-" * 30)
    
    # Prepare tool details as key-value pairs for table display
    tool_details = [
        {"field": "ID", "value": str(tool_data.get('id', 'N/A'))},
        {"field": "Name", "value": str(tool_data.get('name', 'N/A'))},
        {"field": "User ID", "value": str(tool_data.get('user_id', 'N/A'))},
        {"field": "Group ID", "value": str(tool_data.get('group_id', 'N/A'))},
        {"field": "Category", "value": str(tool_data.get('category', 'N/A'))},
        {"field": "Description", "value": str(tool_data.get('description', 'N/A'))},
        {"field": "URL", "value": str(tool_data.get('url', 'N/A'))}
    ]
    
    dynamic_table_print(tool_details, ["field", "value"], ["Field", "Value"])

def print_tools_list(tools_data, args):
    """
    Print list of tools in table format.

    Parameters
    ----------
    tools_data : list
        List of tool dictionaries
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if getattr(args, "json", False):
        json_printer(tools_data)
        return
    elif getattr(args, "jsonl", False):
        jsonl_printer(tools_data)
        return

    if not tools_data:
        print("No tools found.")
        return

    print(f"Found {len(tools_data)} tools:")
    
    # Use the reusable dynamic table formatter
    dynamic_table_print(tools_data, ["id", "name", "category", "description"], ["ID", "Name", "Category", "Description"])
    
    print("-" * 80)
 