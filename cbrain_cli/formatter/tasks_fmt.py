import json

from cbrain_cli.cli_utils import dynamic_table_print, json_printer, jsonl_printer


def print_task_data(tasks_data, args):
    """
    Print task data in either JSON or table format.

    Parameters
    ----------
    tasks_data : list
        List of task data dictionaries
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if getattr(args, "json", False):
        json_printer(tasks_data)
        return
    elif getattr(args, "jsonl", False):
        jsonl_printer(tasks_data)
        return

    if not tasks_data:
        print("No tasks found.")
        return

    # Prepare data with cleaned task types for better display
    formatted_tasks = []
    for task in tasks_data:
        formatted_task = {
            "id": task.get("id", ""),
            "type": task.get("type", "").replace("BoutiquesTask::", ""),
            "status": task.get("status", ""),
            "bourreau_id": task.get("bourreau_id", ""),
            "user_id": task.get("user_id", ""),
            "group_id": task.get("group_id", ""),
        }
        formatted_tasks.append(formatted_task)

    # Use the reusable dynamic table formatter
    dynamic_table_print(
        formatted_tasks,
        ["id", "type", "status", "bourreau_id", "user_id", "group_id"],
        ["ID", "Type", "Status", "Bourreau", "User", "Group"],
    )

    print("-" * 85)
    print(f"Total: {len(tasks_data)} task(s)")

    return


def print_task_details(task_data, args):
    """
    Print detailed information about a specific task.

    Parameters
    ----------
    task_data : dict
        Dictionary containing task details
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if getattr(args, "json", False):
        json_printer(task_data)
        return
    elif getattr(args, "jsonl", False):
        jsonl_printer(task_data)
        return

    # Basic task info
    basic_info = [
        {"field": "ID", "value": str(task_data.get("id", "N/A"))},
        {"field": "Type", "value": str(task_data.get("type", "N/A"))},
        {"field": "Status", "value": str(task_data.get("status", "N/A"))},
    ]

    dynamic_table_print(basic_info, ["field", "value"], ["Field", "Value"])
    print()

    print("OWNERSHIP & ASSIGNMENT")
    print("-" * 30)
    ownership_info = [
        {"field": "User ID", "value": str(task_data.get("user_id", "N/A"))},
        {"field": "Group ID", "value": str(task_data.get("group_id", "N/A"))},
        {"field": "Bourreau ID", "value": str(task_data.get("bourreau_id", "N/A"))},
        {"field": "Tool Config ID", "value": str(task_data.get("tool_config_id", "N/A"))},
        {"field": "Batch ID", "value": str(task_data.get("batch_id", "N/A"))},
    ]

    dynamic_table_print(ownership_info, ["field", "value"], ["Field", "Value"])
    print()

    print("EXECUTION INFO")
    print("-" * 30)
    execution_info = [
        {"field": "Run Number", "value": str(task_data.get("run_number", "N/A"))},
        {
            "field": "Results Data Provider ID",
            "value": str(task_data.get("results_data_provider_id", "N/A")),
        },
        {
            "field": "Cluster Workdir Size",
            "value": str(task_data.get("cluster_workdir_size", "N/A")),
        },
        {"field": "Workdir Archived", "value": str(task_data.get("workdir_archived", "N/A"))},
        {
            "field": "Workdir Archive File ID",
            "value": str(task_data.get("workdir_archive_userfile_id", "N/A")),
        },
    ]

    dynamic_table_print(execution_info, ["field", "value"], ["Field", "Value"])
    print()

    print("TIMESTAMPS")
    print("-" * 30)
    timestamp_info = [
        {"field": "Created At", "value": str(task_data.get("created_at", "N/A"))},
        {"field": "Updated At", "value": str(task_data.get("updated_at", "N/A"))},
    ]

    dynamic_table_print(timestamp_info, ["field", "value"], ["Field", "Value"])

    # Optional fields.
    if task_data.get("description"):
        print()
        print("DESCRIPTION")
        print("-" * 30)
        description = task_data.get("description").strip()
        # Handle multi-line descriptions.
        for line in description.split("\n"):
            print(f"{line}")

    # Display params if they exist.
    if task_data.get("params"):
        print()
        print("PARAMETERS")
        print("-" * 30)
        params_json = json.dumps(task_data.get("params"), indent=2)
        print(params_json)
