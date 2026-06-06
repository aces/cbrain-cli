from cbrain_cli.cli_utils import (
    CliValidationError,
    api_get,
    api_send,
    api_token,
    cbrain_url,
    json_printer,
    pagination,
)


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
    filter_name = getattr(args, "filter_name", None)
    bourreau_id = getattr(args, "bourreau_id", None)

    if filter_name is not None:
        if filter_name != "bourreau-id":
            raise CliValidationError(f"Unsupported filter: {filter_name}", field="filter_name")
        if bourreau_id is None:
            raise CliValidationError(
                "Bourreau ID is required when filter is bourreau-id",
                field="bourreau_id",
            )
        params["bourreau_id"] = str(bourreau_id)
    elif bourreau_id is not None:
        raise CliValidationError(
            "Filter bourreau-id is required when Bourreau ID is specified",
            field="filter_name",
        )

    params = pagination(args, params)
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
        raise CliValidationError("Task ID is required", field="task")
    return api_get(f"{cbrain_url}/tasks/{task_id}", api_token)


def operation_task(args):
    """
    Operation on a task.
    """
    data, _ = api_send(f"{cbrain_url}/tasks/operation", api_token)
    json_printer(data)
