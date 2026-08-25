import json

from cbrain_cli.cli_utils import (
    display_key_value_table,
    dynamic_table_print,
    output_json,
)


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

    if tasks_data is None:
        return

    if not tasks_data:
        print("No tasks found.")
        return

    formatted_tasks = [
        {
            "id": task.get("id", ""),
            "type": (task.get("type") or "").replace("BoutiquesTask::", ""),
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
        for line in str(task_data.get("description", "")).strip().split("\n"):
            print(line)

    # Display params if they exist.
    if task_data.get("params"):
        print()
        print("PARAMETERS")
        print("-" * 30)
        print(json.dumps(task_data.get("params"), indent=2))


def print_task_operation_result(result, args):
    """
    Print the result of a bulk task operation.

    Parameters
    ----------
    result : dict
        Operation result payload from the API
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if output_json(args, result):
        return

    if not result:
        print("No operation result.")
        return

    # Server sometimes returns a single message (e.g. no operation / no tasks).
    if "message" in result and "success_list" not in result:
        print(result["message"])
        return

    operation = getattr(args, "operation", None)
    success = result.get("success_list") or []
    failed = result.get("failed_list") or {}
    skipped = result.get("skipped_list") or {}
    bac_ids = result.get("bac_ids") or []

    print("TASK OPERATION RESULT")
    print("-" * 30)
    if operation:
        print(f"Operation: {operation}")
    print(f"Succeeded: {len(success)}")
    print(f"Skipped:   {sum(len(v) for v in skipped.values())}")
    print(f"Failed:    {sum(len(v) for v in failed.values())}")

    if success:
        print()
        print("SUCCEEDED TASKS")
        print("-" * 30)
        print(", ".join(str(task_id) for task_id in success))

    if skipped:
        print()
        print("SKIPPED")
        print("-" * 30)
        for reason, ids in skipped.items():
            print(f"{reason}: {', '.join(str(i) for i in ids)}")

    if failed:
        print()
        print("FAILED")
        print("-" * 30)
        for reason, ids in failed.items():
            print(f"{reason}: {', '.join(str(i) for i in ids)}")

    if bac_ids:
        print()
        print("BACKGROUND ACTIVITIES")
        print("-" * 30)
        print(", ".join(str(bac_id) for bac_id in bac_ids))
        print("Track with: cbrain background show <id>")
