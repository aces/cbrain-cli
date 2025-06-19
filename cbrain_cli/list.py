import json
import urllib.request
from cbrain_cli.config import auth_headers
from cbrain_cli.cli_utils import cbrain_url, api_token

def list_projects(args):
    """
    List all projects/groups from CBRAIN.
    
    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag
        
    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    
    # Prepare the API request.
    groups_endpoint = f"{cbrain_url}/groups"
    headers = auth_headers(api_token)
    
    # Create the request.
    request = urllib.request.Request(
        groups_endpoint,
        data=None,
        headers=headers,
        method='GET'
    )
    
    # Make the request.
    with urllib.request.urlopen(request) as response:
        data = response.read().decode('utf-8')
        projects_data = json.loads(data)
    
    # Output in requested format.
    if getattr(args, 'json', False):
        # JSON format.
        formatted_data = []
        for project in projects_data:
            formatted_data.append({
                "id": project.get("id"),
                "type": project.get("type"),
                "name": project.get("name")
            })
        print(json.dumps(formatted_data, indent=2))
    else:
        # Table format.
        print("ID Type        Project Name")
        print("-- ----------- ----------------")
        for project in projects_data:
            project_id = project.get("id", "")
            project_type = project.get("type", "")
            project_name = project.get("name", "")
            print(f"{project_id:<2} {project_type:<11} {project_name}")
    
    return 

def list_files(args):
    """
    List all files from CBRAIN.
    
    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag
        
    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    # Prepare the API request.
    userfiles_endpoint = f"{cbrain_url}/userfiles"
    headers = auth_headers(api_token)
    
    # Create the request.
    request = urllib.request.Request(
        userfiles_endpoint,
        data=None,
        headers=headers,
        method='GET'
    )
    
    # Make the request.
    with urllib.request.urlopen(request) as response:
        data = response.read().decode('utf-8')
        files_data = json.loads(data)
    
    # Output in requested format.
    if getattr(args, 'json', False):
        print(json.dumps(files_data, indent=2))
    else:
        # Table format.
        print("ID   Type        File Name")
        print("---- ----------- -----------------------")
        for file_item in files_data:
            file_id = file_item.get("id", "")
            file_type = file_item.get("type", "")
            file_name = file_item.get("name", "")
            print(f"{file_id:<4} {file_type:<11} {file_name}")
    
    return 
