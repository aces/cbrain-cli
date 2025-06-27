import json
import urllib.parse
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url
from cbrain_cli.config import auth_headers


def list_tasks(args):
    """
    List all tasks from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag and optional bourreau_id filter

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    # Build query parameters for filtering.
    query_params = {}
    
    # Add filter if provided.
    if hasattr(args, "filter_type") and args.filter_type is not None:
        if args.filter_value is None:
            print("Error: Filter value is required when filter type is specified")
            return 1
        if args.filter_type == "bourreau_id":
            query_params["bourreau_id"] = str(args.filter_value)
    elif hasattr(args, "filter_value") and args.filter_value is not None:
        print("Error: Filter type is required when filter value is specified")
        return 1

    # Prepare the API request.
    tasks_endpoint = f"{cbrain_url}/tasks"
    
    # Add query parameters if any filters are provided.
    if query_params:
        query_string = urllib.parse.urlencode(query_params)
        tasks_endpoint = f"{tasks_endpoint}?{query_string}"

    headers = auth_headers(api_token)

    # Create the request.
    request = urllib.request.Request(
        tasks_endpoint, data=None, headers=headers, method="GET"
    )

    # Make the request.
    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        tasks_data = json.loads(data)

    # Output in requested format.
    if getattr(args, "json", False):
        print(json.dumps(tasks_data, indent=2))
    else:
        # Table format.
        if not tasks_data:
            print("No tasks found.")
            return
            
        print(f"{'ID':<6} {'Type':<30} {'Status':<12} {'Bourreau':<10} {'User':<6} {'Group':<6}")
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
            print(f"{task_id:<6} {task_type:<30} {task_status:<12} {bourreau_id:<10} {user_id:<6} {group_id:<6}")
        print("-" * 85)
        print(f"Total: {len(tasks_data)} task(s)")

    return


def show_task(args):
    """
    Show detailed information about a specific task from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the task argument with task_id

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    # Get the task ID from the task argument.
    task_id = getattr(args, "task", None)
    if not task_id:
        print("Error: Task ID is required")
        return 1

    # Prepare the API request.
    task_endpoint = f"{cbrain_url}/tasks/{task_id}"
    headers = auth_headers(api_token)

    # Create the request.
    request = urllib.request.Request(
        task_endpoint, data=None, headers=headers, method="GET"
    )

    # Make the request.     
    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            task_data = json.loads(data)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: Task with ID {task_id} not found")
            return 1
        else:
            print(f"Error: HTTP {e.code} - {e.reason}")
            return 1

    # Output the task details.
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
    print(f"Results Data Provider ID:  {task_data.get('results_data_provider_id', 'N/A')}")
    print(f"Cluster Workdir Size:      {task_data.get('cluster_workdir_size', 'N/A')}")
    print(f"Workdir Archived:          {task_data.get('workdir_archived', 'N/A')}")
    print(f"Workdir Archive File ID:   {task_data.get('workdir_archive_userfile_id', 'N/A')}")
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
        description = task_data.get('description').strip()
        # Handle multi-line descriptions.
        for line in description.split('\n'):
            print(f"{line}")
    
    # Display params if they exist.
    if task_data.get("params"):
        print()
        print("PARAMETERS")
        print("-" * 30)
        params_json = json.dumps(task_data.get("params"), indent=2)
        print(params_json)

    return 0
