from cbrain_cli.cli_utils import display_key_value_table, dynamic_table_print, output_json


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
    if output_json(args, provider_data):
        return

    print("DATA PROVIDER DETAILS")
    print("-" * 30)
    display_key_value_table(
        [
            ("ID", str(provider_data.get("id", "N/A"))),
            ("Name", str(provider_data.get("name", "N/A"))),
            ("Type", str(provider_data.get("type", "N/A"))),
            ("Description", str(provider_data.get("description", "N/A"))),
        ]
    )
    print()

    print("CONNECTION INFO")
    print("-" * 30)
    display_key_value_table(
        [
            ("Remote User", str(provider_data.get("remote_user", "N/A"))),
            ("Remote Host", str(provider_data.get("remote_host", "N/A"))),
            ("Remote Directory", str(provider_data.get("remote_dir", "N/A"))),
            ("Remote Port", str(provider_data.get("remote_port", "N/A"))),
        ]
    )
    print()

    print("OWNERSHIP & STATUS")
    print("-" * 30)
    display_key_value_table(
        [
            ("User ID", str(provider_data.get("user_id", "N/A"))),
            ("Group ID", str(provider_data.get("group_id", "N/A"))),
            ("Online", str(provider_data.get("online", "N/A"))),
            ("Read Only", str(provider_data.get("read_only", "N/A"))),
            ("Is Browsable", str(provider_data.get("is_browsable", "N/A"))),
            ("Is Fast Syncing", str(provider_data.get("is_fast_syncing", "N/A"))),
            ("Allow File Owner Change", str(provider_data.get("allow_file_owner_change", "N/A"))),
            (
                "Content Storage Shared Between Users",
                str(provider_data.get("content_storage_shared_between_users", "N/A")),
            ),
        ]
    )


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
    if output_json(args, providers_data):
        return

    if providers_data is None:
        return

    if not providers_data:
        print("No data providers found.")
        return

    formatted_providers = [
        {
            "id": p.get("id", ""),
            "name": p.get("name", ""),
            "type": p.get("type", ""),
            "remote_host": p.get("remote_host", ""),
            "online": "Yes" if p.get("online", False) else "No",
        }
        for p in providers_data
    ]

    dynamic_table_print(
        formatted_providers,
        ["id", "name", "type", "remote_host", "online"],
        ["ID", "Name", "Type", "Host", "Online"],
    )
