from cbrain_cli.cli_utils import json_printer

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

    print(
        f"id: {provider_data.get('id', 'N/A')}\n"
        f"name: {provider_data.get('name', 'N/A')}\n"
        f"type: {provider_data.get('type', 'N/A')}\n"
        f"remote_user: {provider_data.get('remote_user', 'N/A')}\n"
        f"remote_host: {provider_data.get('remote_host', 'N/A')}\n"
        f"remote_dir: {provider_data.get('remote_dir', 'N/A')}\n"
        f"remote_port: {provider_data.get('remote_port', 'N/A')}\n"
        f"user_id: {provider_data.get('user_id', 'N/A')}\n"
        f"group_id: {provider_data.get('group_id', 'N/A')}\n"
        f"online: {provider_data.get('online', 'N/A')}\n"
        f"read_only: {provider_data.get('read_only', 'N/A')}\n"
        f"is_browsable: {provider_data.get('is_browsable', 'N/A')}\n"
        f"is_fast_syncing: {provider_data.get('is_fast_syncing', 'N/A')}\n"
        f"allow_file_owner_change: {provider_data.get('allow_file_owner_change', 'N/A')}\n"
        f"content_storage_shared_between_users: {provider_data.get('content_storage_shared_between_users', 'N/A')}\n"
        f"description: {provider_data.get('description', 'N/A')}\n"
    )

def print_providers_list(providers_data, args):
    """
    Print list of data providers in table format.

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
 
    print(
        "ID   Name                 Type                            Host              Online"
    )
    print(
        "---- -------------------- ------------------------------- ----------------- ------"
    )
    for provider in providers_data:
        provider_id = provider.get("id", "")
        provider_name = provider.get("name", "")
        provider_type = provider.get("type", "")
        provider_host = provider.get("remote_host", "")
        provider_online = "Yes" if provider.get("online", False) else "No"
        print(
            f"{provider_id:<4} {provider_name:<20} {provider_type:<31} {provider_host:<17} {provider_online}"
        )
