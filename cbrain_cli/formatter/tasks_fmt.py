import json

from cbrain_cli.cli_utils import json_printer, jsonl_printer

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
    else:
        # Table format.
        if not tasks_data:
            print("No tasks found.")
            return

        print(
            f"{'ID':<6} {'Type':<30} {'Status':<12} {'Bourreau':<10} {'User':<6} {'Group':<6}"
        )
        print("-" * 85)
        for task in tasks_data:
            task_id = str(task.get("id", ""))
            task_type = task.get("type", "").replace("BoutiquesTask::", "")
            # Truncate long task types.
            if len(task_type) > 29:
                task_type = task_type[:26] + "..."
            task_status = task.get("status", "")
            bourreau_id = str(task.get("bourreau_id", ""))
            user_id = str(task.get("user_id", ""))
            group_id = str(task.get("group_id", ""))
            print(
                f"{task_id:<6} {task_type:<30} {task_status:<12} {bourreau_id:<10} {user_id:<6} {group_id:<6}"
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

    print(f"ID:                        {task_data.get('id', 'N/A')}")
    print(f"Type:                      {task_data.get('type', 'N/A')}")
    print(f"Status:                    {task_data.get('status', 'N/A')}")
    print()

    print("OWNERSHIP & ASSIGNMENT")
    print("-" * 30)
    print(f"User ID:                   {task_data.get('user_id', 'N/A')}")
    print(f"Group ID:                  {task_data.get('group_id', 'N/A')}")
    print(f"Bourreau ID:               {task_data.get('bourreau_id', 'N/A')}")
    print(f"Tool Config ID:            {task_data.get('tool_config_id', 'N/A')}")
    print(f"Batch ID:                  {task_data.get('batch_id', 'N/A')}")
    print()

    print("EXECUTION INFO")
    print("-" * 30)
    print(f"Run Number:                {task_data.get('run_number', 'N/A')}")
    print(
        f"Results Data Provider ID:  {task_data.get('results_data_provider_id', 'N/A')}"
    )
    print(f"Cluster Workdir Size:      {task_data.get('cluster_workdir_size', 'N/A')}")
    print(f"Workdir Archived:          {task_data.get('workdir_archived', 'N/A')}")
    print(
        f"Workdir Archive File ID:   {task_data.get('workdir_archive_userfile_id', 'N/A')}"
    )
    print()

    print("TIMESTAMPS")
    print("-" * 30)
    print(f"Created At:                {task_data.get('created_at', 'N/A')}")
    print(f"Updated At:                {task_data.get('updated_at', 'N/A')}")

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