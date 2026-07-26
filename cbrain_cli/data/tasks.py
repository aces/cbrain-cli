from cbrain_cli.cli_utils import (
    CbrainClient,
    CliValidationError,
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
    list
        List of task dictionaries
    """
    params = {}
    filter_name = getattr(args, "filter_name", None)
    bourreau_id = getattr(args, "bourreau_id", None)

    if filter_name is not None:
        if filter_name != "bourreau_id":
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
    return CbrainClient.from_credentials().get("/tasks", params=params)


def show_task(args):
    """
    Show detailed information about a specific task from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the task argument with task_id

    Returns
    -------
    dict
        Task details dictionary
    """
    task_id = getattr(args, "task", None)
    if not task_id:
        raise CliValidationError("Task ID is required", field="task")
    return CbrainClient.from_credentials().get(f"/tasks/{task_id}")


def operation_task(args):
    """
    Operation on a task.
    """
    data, _ = CbrainClient.from_credentials().send("POST", "/tasks/operation")
    json_printer(data)
