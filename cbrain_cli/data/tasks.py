from cbrain_cli.cli_utils import (
    CbrainClient,
    CliValidationError,
    pagination,
)

# Names accepted by CBRAIN POST /tasks/operation
TASK_OPERATIONS = (
    "terminate",
    "archive",
    "archive_file",
    "unarchive",
    "zap_wd",
    "save_wd",
    "hold",
    "release",
    "suspend",
    "resume",
    "duplicate",
    "recover",
    "restart_setup",
    "restart_cluster",
    "restart_postprocess",
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
    Run a bulk operation on tasks.
    """
    operation = getattr(args, "operation", None)
    if not operation:
        raise CliValidationError("Operation is required", field="operation")
    if operation not in TASK_OPERATIONS:
        raise CliValidationError(
            f"Unsupported operation: {operation}",
            field="operation",
        )

    task_ids = getattr(args, "task_id", None) or []
    batch_ids = getattr(args, "batch_id", None) or []
    if not task_ids and not batch_ids:
        raise CliValidationError(
            "At least one --task-id or --batch-id is required",
            field="--task-id",
        )

    payload = {"operation": operation}
    if task_ids:
        payload["tasklist"] = list(task_ids)
    if batch_ids:
        payload["batch_ids"] = list(batch_ids)

    dup_bourreau_id = getattr(args, "dup_bourreau_id", None)
    if dup_bourreau_id is not None:
        payload["dup_bourreau_id"] = dup_bourreau_id
    archive_dp_id = getattr(args, "archive_dp_id", None)
    if archive_dp_id is not None:
        payload["archive_dp_id"] = archive_dp_id
    if getattr(args, "nozip", False):
        payload["nozip"] = True

    data, _ = CbrainClient.from_credentials().send("POST", "/tasks/operation", payload=payload)
    return data
