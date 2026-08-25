from cbrain_cli.cli_utils import display_key_value_table, dynamic_table_print, output_json


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
    if projects_data is None:
        return

    formatted_data = [
        {"id": p.get("id"), "type": p.get("type"), "name": p.get("name")} for p in projects_data
    ]

    if output_json(args, formatted_data):
        return

    if not formatted_data:
        print("No projects found.")
        return

    dynamic_table_print(formatted_data, ["id", "type", "name"], ["ID", "Type", "Project Name"])


def print_current_project(project_data, args=None):
    """
    Print current project details.

    Parameters
    ----------
    project_data : dict
        Dictionary containing project name and ID
    args : argparse.Namespace, optional
        Command line arguments, including the --json flag
    """
    if args is not None and output_json(args, project_data):
        return

    group_name = project_data.get("name", "Unknown")
    group_id = project_data.get("id")
    print(f'Current project is "{group_name}" ID={group_id}')


def print_project_details(project_data, args):
    """
    Print detailed information about a specific project.

    Parameters
    ----------
    project_data : dict
        Dictionary containing project details
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if output_json(args, project_data):
        return

    print("PROJECT DETAILS")
    print("-" * 30)
    display_key_value_table(
        [
            ("ID", str(project_data.get("id", "N/A"))),
            ("Name", str(project_data.get("name", "N/A"))),
            ("Type", str(project_data.get("type", "N/A"))),
            ("Site ID", str(project_data.get("site_id", "N/A"))),
            ("Invisible", str(project_data.get("invisible", "N/A"))),
        ]
    )

    if project_data.get("description"):
        print()
        print("DESCRIPTION")
        print("-" * 30)
        for line in project_data.get("description").strip().split("\n"):
            print(line)


def print_no_project(args=None):
    """
    Print message when no current project is set.

    Parameters
    ----------
    args : argparse.Namespace, optional
        Command line arguments, including the --json flag
    """
    result = {"current_group_id": None, "current_group_name": None}
    if args is not None and output_json(args, result):
        return

    print("No current project set. Use 'cbrain project switch <ID>' to set a project.")


def print_unswitch_result(result, args):
    """
    Print the result of clearing the current project context.

    Parameters
    ----------
    result : dict
        Unswitch result with previous and current group identifiers
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if output_json(args, result):
        return

    previous_group_id = result.get("previous_group_id")
    if previous_group_id:
        previous_group_name = result.get("previous_group_name", "Unknown")
        print(f'Cleared current project "{previous_group_name}" ID={previous_group_id}')
    else:
        print("No current project set. Use 'cbrain project switch <ID>' to set a project.")
