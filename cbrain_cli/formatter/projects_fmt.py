from cbrain_cli.cli_utils import dynamic_table_print, json_printer, jsonl_printer


def print_projects_list(projects_data, args):
    """
    Print table of projects.

    Parameters
    ----------
    projects_data : list
        List of project dictionaries
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    formatted_data = [
        {
            "id": project.get("id"),
            "type": project.get("type"),
            "name": project.get("name"),
        }
        for project in projects_data
    ]

    if getattr(args, "json", False):
        json_printer(formatted_data)
        return
    elif getattr(args, "jsonl", False):
        jsonl_printer(formatted_data)
        return

    dynamic_table_print(projects_data, ["id", "type", "name"], ["ID", "Type", "Project Name"])


def print_current_project(project_data):
    """
    Print current project details.

    Parameters
    ----------
    project_data : dict
        Dictionary containing project name and ID
    """
    group_name = project_data.get("name", "Unknown")
    group_id = project_data.get("id")
    print(f'Current project is "{group_name}" ID={group_id}')


def print_no_project():
    """
    Print message when no current project is set.
    """
    print("No current project set. Use 'cbrain project switch <ID>' to set a project.")
