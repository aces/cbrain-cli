from cbrain_cli.cli_utils import json_printer

def print_projects_list(projects_data, args):
    """
    Print list of projects in table format.

    Parameters
    ----------
    projects_data : list
        List of project dictionaries
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if getattr(args, "json", False):
        formatted_data = []
        for project in projects_data:
            formatted_data.append(
                {
                    "id": project.get("id"),
                    "type": project.get("type"),
                    "name": project.get("name"),
                }
            )
        json_printer(formatted_data)
        return

    print("ID Type        Project Name")
    print("-- ----------- ----------------")
    for project in projects_data:
        project_id = project.get("id", "")
        project_type = project.get("type", "")
        project_name = project.get("name", "")
        print(f"{project_id:<2} {project_type:<11} {project_name}")

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
