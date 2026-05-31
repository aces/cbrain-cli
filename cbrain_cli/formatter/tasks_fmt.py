import json

from cbrain_cli.cli_utils import dynamic_table_print, display_key_value_table, output_json


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
    if output_json(args, tasks_data):
        return

    if not tasks_data:
        print("No tasks found.")
        return

    formatted_tasks = [
        {
            "id": task.get("id", ""),
            "type": task.get("type", "").replace("BoutiquesTask::", ""),
            "status": task.get("status", ""),
            "bourreau_id": task.get("bourreau_id", ""),
            "user_id": task.get("user_id", ""),
            "group_id": task.get("group_id", ""),
        }
        for task in tasks_data
    ]

    dynamic_table_print(
        formatted_tasks,
        ["id", "type", "status", "bourreau_id", "user_id", "group_id"],
        ["ID", "Type", "Status", "Bourreau", "User", "Group"],
    )

    print("-" * 85)
    print(f"Total: {len(tasks_data)} task(s)")


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
    if output_json(args, task_data):
        return

    display_key_value_table(
        [
            ("ID", str(task_data.get("id", "N/A"))),
            ("Type", str(task_data.get("type", "N/A"))),
            ("Status", str(task_data.get("status", "N/A"))),
        ]
    )
    print()

    print("OWNERSHIP & ASSIGNMENT")
    print("-" * 30)
    display_key_value_table(
        [
            ("User ID", str(task_data.get("user_id", "N/A"))),
            ("Group ID", str(task_data.get("group_id", "N/A"))),
            ("Bourreau ID", str(task_data.get("bourreau_id", "N/A"))),
            ("Tool Config ID", str(task_data.get("tool_config_id", "N/A"))),
            ("Batch ID", str(task_data.get("batch_id", "N/A"))),
        ]
    )
    print()

    print("EXECUTION INFO")
    print("-" * 30)
    display_key_value_table(
        [
            ("Run Number", str(task_data.get("run_number", "N/A"))),
            ("Results Data Provider ID", str(task_data.get("results_data_provider_id", "N/A"))),
            ("Cluster Workdir Size", str(task_data.get("cluster_workdir_size", "N/A"))),
            ("Workdir Archived", str(task_data.get("workdir_archived", "N/A"))),
            ("Workdir Archive File ID", str(task_data.get("workdir_archive_userfile_id", "N/A"))),
        ]
    )
    print()

    print("TIMESTAMPS")
    print("-" * 30)
    display_key_value_table(
        [
            ("Created At", str(task_data.get("created_at", "N/A"))),
            ("Updated At", str(task_data.get("updated_at", "N/A"))),
        ]
    )

    if task_data.get("description"):
        print()
        print("DESCRIPTION")
        print("-" * 30)
        for line in task_data.get("description").strip().split("\n"):
            print(line)

    # Display params if they exist.
    if task_data.get("params"):
        print()
        print("PARAMETERS")
        print("-" * 30)
        print(json.dumps(task_data.get("params"), indent=2))
