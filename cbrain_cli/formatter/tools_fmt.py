from cbrain_cli.cli_utils import display_key_value_table, dynamic_table_print, output_json


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
    if output_json(args, tool_data):
        return

    print("TOOL DETAILS")
    print("-" * 30)
    display_key_value_table(
        [
            ("ID", str(tool_data.get("id", "N/A"))),
            ("Name", str(tool_data.get("name", "N/A"))),
            ("User ID", str(tool_data.get("user_id", "N/A"))),
            ("Group ID", str(tool_data.get("group_id", "N/A"))),
            ("Category", str(tool_data.get("category", "N/A"))),
            ("Description", str(tool_data.get("description", "N/A"))),
            ("URL", str(tool_data.get("url", "N/A"))),
        ]
    )


def print_tools_list(tools_data, args):
    """
    Print table of tools.

    Parameters
    ----------
    tools_data : list
        List of tool dictionaries
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if output_json(args, tools_data):
        return

    if tools_data is None:
        return

    if not tools_data:
        print("No tools found.")
        return

    print(f"Found {len(tools_data)} tools:")

    # Use the reusable dynamic table formatter with wrapping for long descriptions.
    # - Wrap the 'description' column to fit terminal width.
    # - Constrain 'ID' to the max width needed for IDs visible; other columns can grow.
    dynamic_table_print(
        tools_data,
        ["id", "name", "category", "description"],
        ["ID", "Name", "Category", "Description"],
        wrap_columns=["description"],
        max_column_widths={"id": 8},
        indent_wrapped=True,
        max_row_lines=3,
    )

    print("-" * 80)
