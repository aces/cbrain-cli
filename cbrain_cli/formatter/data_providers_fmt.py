from cbrain_cli.cli_utils import dynamic_table_print, json_printer, jsonl_printer


def print_provider_details(provider_data, args):
    """
    Print detailed information about a specific data provider.

    Parameters
    ----------
    provider_data : dict
        Dictionary containing data provider details
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if getattr(args, "json", False):
        json_printer(provider_data)
        return
    elif getattr(args, "jsonl", False):
        jsonl_printer(provider_data)
        return

    print("DATA PROVIDER DETAILS")
    print("-" * 30)

    # Basic information
    basic_info = [
        {"field": "ID", "value": str(provider_data.get("id", "N/A"))},
        {"field": "Name", "value": str(provider_data.get("name", "N/A"))},
        {"field": "Type", "value": str(provider_data.get("type", "N/A"))},
        {"field": "Description", "value": str(provider_data.get("description", "N/A"))},
    ]

    dynamic_table_print(basic_info, ["field", "value"], ["Field", "Value"])
    print()

    print("CONNECTION INFO")
    print("-" * 30)

    # Connection information
    connection_info = [
        {"field": "Remote User", "value": str(provider_data.get("remote_user", "N/A"))},
        {"field": "Remote Host", "value": str(provider_data.get("remote_host", "N/A"))},
        {"field": "Remote Directory", "value": str(provider_data.get("remote_dir", "N/A"))},
        {"field": "Remote Port", "value": str(provider_data.get("remote_port", "N/A"))},
    ]

    dynamic_table_print(connection_info, ["field", "value"], ["Field", "Value"])
    print()

    print("OWNERSHIP & STATUS")
    print("-" * 30)

    # Ownership and status information
    status_info = [
        {"field": "User ID", "value": str(provider_data.get("user_id", "N/A"))},
        {"field": "Group ID", "value": str(provider_data.get("group_id", "N/A"))},
        {"field": "Online", "value": str(provider_data.get("online", "N/A"))},
        {"field": "Read Only", "value": str(provider_data.get("read_only", "N/A"))},
        {"field": "Is Browsable", "value": str(provider_data.get("is_browsable", "N/A"))},
        {"field": "Is Fast Syncing", "value": str(provider_data.get("is_fast_syncing", "N/A"))},
        {
            "field": "Allow File Owner Change",
            "value": str(provider_data.get("allow_file_owner_change", "N/A")),
        },
        {
            "field": "Content Storage Shared Between Users",
            "value": str(provider_data.get("content_storage_shared_between_users", "N/A")),
        },
    ]

    dynamic_table_print(status_info, ["field", "value"], ["Field", "Value"])


def print_providers_list(providers_data, args):
    """
    Print table of data providers.

    Parameters
    ----------
    providers_data : list
        List of data provider dictionaries
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if getattr(args, "json", False):
        json_printer(providers_data)
        return
    elif getattr(args, "jsonl", False):
        jsonl_printer(providers_data)
        return

    if not providers_data:
        print("No data providers found.")
        return

    formatted_providers = []
    for provider in providers_data:
        formatted_provider = {
            "id": provider.get("id", ""),
            "name": provider.get("name", ""),
            "type": provider.get("type", ""),
            "remote_host": provider.get("remote_host", ""),
            "online": "Yes" if provider.get("online", False) else "No",
        }
        formatted_providers.append(formatted_provider)

    dynamic_table_print(
        formatted_providers,
        ["id", "name", "type", "remote_host", "online"],
        ["ID", "Name", "Type", "Host", "Online"],
    )
