from cbrain_cli.cli_utils import json_printer

def print_resources_list(resources_data, args):
    """
    Print list of remote resources in table format.

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

    # Table format.
    if not resources_data:
        print("No remote resources found.")
        return

    print("REMOTE RESOURCES (EXECUTION SERVERS)")
    print("-" * 80)
    print(
        f"{'ID':<6} {'Name':<25} {'User':<6} {'Group':<6} {'Online':<8} {'Read-Only':<10}"
    )
    print("-" * 80)
    for bourreau in resources_data:
        bourreau_id = str(bourreau.get("id", ""))
        bourreau_name = bourreau.get("name", "")
        # Truncate long names.
        if len(bourreau_name) > 24:
            bourreau_name = bourreau_name[:21] + "..."
        user_id = str(bourreau.get("user_id", ""))
        group_id = str(bourreau.get("group_id", ""))
        online = "Yes" if bourreau.get("online", False) else "No"
        read_only = "Yes" if bourreau.get("read_only", False) else "No"
        print(
            f"{bourreau_id:<6} {bourreau_name:<25} {user_id:<6} {group_id:<6} {online:<8} {read_only:<10}"
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
    if getattr(args, "json", False):
        json_printer(resource_data)
        return

    print("REMOTE RESOURCE DETAILS")
    print("-" * 30)
    print(f"ID:                        {resource_data.get('id', 'N/A')}")
    print(f"Name:                      {resource_data.get('name', 'N/A')}")
    print(f"Type:                      {resource_data.get('type', 'N/A')}")
    print()

    print("OWNERSHIP & ACCESS")
    print("-" * 30)
    print(f"User ID:                   {resource_data.get('user_id', 'N/A')}")
    print(f"Group ID:                  {resource_data.get('group_id', 'N/A')}")
    print(f"Online:                    {resource_data.get('online', 'N/A')}")
    print(f"Read Only:                 {resource_data.get('read_only', 'N/A')}")
    print() 