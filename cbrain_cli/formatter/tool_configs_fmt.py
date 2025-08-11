from cbrain_cli.cli_utils import json_printer, jsonl_printer, dynamic_table_print

def print_tool_configs_list(tool_configs, args):
    """
    Pretty print a list of tool configurations.
    """
    if getattr(args, "json", False):
        json_printer(tool_configs)
        return
    elif getattr(args, "jsonl", False):
        jsonl_printer(tool_configs)
        return

    if not tool_configs:
        print("No tool configurations found.")
        return

    # Prepare data for better display
    formatted_configs = []
    for config in tool_configs:
        formatted_config = {
            "id": config.get("id", ""),
            "version_name": config.get("version_name", ""),
            "tool_id": config.get("tool_id", ""),
            "bourreau_id": config.get("bourreau_id", ""),
            "group_id": config.get("group_id", ""),
            "ncpus": config.get("ncpus", "1"),
            "description": config.get("description", "")
        }
        formatted_configs.append(formatted_config)
    
    # Use the reusable dynamic table formatter
    dynamic_table_print(formatted_configs, 
                       ["id", "version_name", "tool_id", "bourreau_id", "group_id", "ncpus", "description"],
                       ["ID", "Version", "Tool ID", "Bourreau", "Group", "CPUs", "Description"])
    
    print("-" * 85)
    print(f"Total: {len(tool_configs)} configuration(s)")

def print_tool_config_details(tool_config, args):
    """
    Pretty print the details of a tool configuration.
    """
    if not tool_config:
        print("No tool configuration found.")
        return
    json_printer(tool_config)

def print_boutiques_descriptor(boutiques_descriptor, args):
    """
    Pretty print the Boutiques descriptor for a tool configuration.
    """
    if not boutiques_descriptor:
        print("No Boutiques descriptor found.")
        return

    json_printer(boutiques_descriptor)
