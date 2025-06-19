import json
import urllib.request
from cbrain_cli.config import auth_headers
from cbrain_cli.cli_utils import cbrain_url, api_token

def show_file(args):
    """
    Show detailed information about a specific file from CBRAIN.
    
    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the show argument with file_id
    """
    
    # Get the file ID from the --show argument.
    file_id = getattr(args, 'show', None)
    if not file_id:
        print("Error: File ID is required")
        return 1
    
    # Prepare the API request.
    userfile_endpoint = f"{cbrain_url}/userfiles/{file_id}"
    headers = auth_headers(api_token)
    
    # Create the request.
    request = urllib.request.Request(
        userfile_endpoint,
        data=None,
        headers=headers,
        method='GET'
    )
    
    # Make the request.
    with urllib.request.urlopen(request) as response:
        data = response.read().decode('utf-8')
        file_data = json.loads(data)
    
    # Output the file details.
    print(f"id: {file_data.get('id', 'N/A')}\n"
            f"type: {file_data.get('type', 'N/A')}\n"
            f"name: {file_data.get('name', 'N/A')}\n"
            f"data_provider: {file_data.get('data_provider_id', 'N/A')}\n"
            f"size: {file_data.get('size', 'N/A')}\n"
            f"num_files: {file_data.get('num_files', 'N/A')}\n"
            f"user_id: {file_data.get('user_id', 'N/A')}\n"
            f"group_id: {file_data.get('group_id', 'N/A')}")
    
    # Optional fields.
    if file_data.get('description'):
        print(f"description: {file_data.get('description')}")
    if file_data.get('hidden'):
        print(f"hidden: {file_data.get('hidden')}")
    if file_data.get('immutable'):
        print(f"immutable: {file_data.get('immutable')}")
    if file_data.get('archived'):
        print(f"archived: {file_data.get('archived')}")
    
    return 0
