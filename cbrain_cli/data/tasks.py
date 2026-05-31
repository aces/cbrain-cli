from cbrain_cli.cli_utils import api_get, api_send, api_token, cbrain_url, json_printer, pagination


def list_tasks(args):
    """
    List all tasks from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag and optional bourreau_id filter

    Returns
    -------
    list or None
        List of task dictionaries, or None on error
    """
    params = {}

    if hasattr(args, "filter_type") and args.filter_type is not None:
        if args.filter_value is None:
            print("Error: Filter value is required when filter type is specified")
            return None
        if args.filter_type == "bourreau_id":
            params["bourreau_id"] = str(args.filter_value)
    elif hasattr(args, "filter_value") and args.filter_value is not None:
        print("Error: Filter type is required when filter value is specified")
        return None

    params = pagination(args, params)
    if params is None:
        return None
    return api_get(f"{cbrain_url}/tasks", api_token, params)


def show_task(args):
    """
    Show detailed information about a specific task from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the task argument with task_id

    Returns
    -------
    dict or None
        Task details dictionary, or None on error
    """
    task_id = getattr(args, "task", None)
    if not task_id:
        print("Error: Task ID is required")
        return None
    return api_get(f"{cbrain_url}/tasks/{task_id}", api_token)


def operation_task(args):
    """
    Operation on a task.
    """
    data, _ = api_send(f"{cbrain_url}/tasks/operation", api_token)
    json_printer(data)
