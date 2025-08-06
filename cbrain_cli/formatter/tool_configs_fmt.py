from cbrain_cli.cli_utils import json_printer, jsonl_printer

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
    else:
        # Table format.
        if not tool_configs:
            print("No tool configurations found.")
            return

        print(f"{'ID':<6} {'Version':<12} {'Tool ID':<8} {'Bourreau':<10} {'Group':<6} {'CPUs':<6} {'Description':<30}")
        print("-" * 85)
        for config in tool_configs:
            config_id = str(config.get("id", ""))
            version = str(config.get("version_name", ""))
            tool_id = str(config.get("tool_id", ""))
            bourreau_id = str(config.get("bourreau_id", ""))
            group_id = str(config.get("group_id", ""))
            ncpus = str(config.get("ncpus", "1"))
            description = config.get("description", "")
            # Truncate long descriptions
            if len(description) > 29:
                description = description[:26] + "..."
            
            print(f"{config_id:<6} {version:<12} {tool_id:<8} {bourreau_id:<10} {group_id:<6} {ncpus:<6} {description:<30}")
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
