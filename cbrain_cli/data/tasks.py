import json
import urllib.parse
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url, json_printer, pagination
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

    query_params = pagination(args, query_params)

    tasks_endpoint = f"{cbrain_url}/tasks"

    if query_params:
        query_string = urllib.parse.urlencode(query_params)
        tasks_endpoint = f"{tasks_endpoint}?{query_string}"

    headers = auth_headers(api_token)

    request = urllib.request.Request(tasks_endpoint, data=None, headers=headers, method="GET")

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        tasks_data = json.loads(data)

    return tasks_data


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

    task_endpoint = f"{cbrain_url}/tasks/{task_id}"
    headers = auth_headers(api_token)

    request = urllib.request.Request(task_endpoint, data=None, headers=headers, method="GET")

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        task_data = json.loads(data)

    return task_data


def operation_task(args):
    """
    Operation on a task.
    """
    operate_task_endpoint = f"{cbrain_url}/tasks/operation"
    headers = auth_headers(api_token)

    request = urllib.request.Request(
        operate_task_endpoint, data=None, headers=headers, method="POST"
    )

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        json_printer(data)
