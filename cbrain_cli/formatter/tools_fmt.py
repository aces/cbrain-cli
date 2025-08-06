from cbrain_cli.cli_utils import json_printer, jsonl_printer

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
    print(
        f"id: {tool_data.get('id', 'N/A')}\n"
        f"name: {tool_data.get('name', 'N/A')}\n"
        f"user_id: {tool_data.get('user_id', 'N/A')}\n"
        f"group_id: {tool_data.get('group_id', 'N/A')}\n"
        f"category: {tool_data.get('category', 'N/A')}\n"
        f"description: {tool_data.get('description', 'N/A')}\n"
        f"url: {tool_data.get('url', 'N/A')}\n"
    )

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
    print(f"{'ID':<5} {'Name':<20} {'Category':<20} {'Description':<30}")
    print("-" * 80)
    for tool in tools_data:
        tool_id = str(tool.get("id", "N/A"))
        name = tool.get("name", "N/A")[:19]
        category = tool.get("category", "N/A")[:19]
        description = tool.get("description", "N/A")[:29]
        print(f"{tool_id:<5} {name:<20} {category:<20} {description:<30}")
 