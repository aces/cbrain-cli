from cbrain_cli.cli_utils import json_printer, jsonl_printer, dynamic_table_print

def print_file_details(file_data, args):
    """
    Print detailed information about a specific file.

    Parameters
    ----------
    file_data : dict
        Dictionary containing file details
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if getattr(args, "json", False):
        json_printer(file_data)
        return
    elif getattr(args, "jsonl", False):
        jsonl_printer(file_data)
        return
    print(
        f"id: {file_data.get('id', 'N/A')}\n"
        f"type: {file_data.get('type', 'N/A')}\n"
        f"name: {file_data.get('name', 'N/A')}\n"
        f"data_provider: {file_data.get('data_provider_id', 'N/A')}\n"
        f"size: {file_data.get('size', 'N/A')}\n"
        f"num_files: {file_data.get('num_files', 'N/A')}\n"
        f"user_id: {file_data.get('user_id', 'N/A')}\n"
        f"group_id: {file_data.get('group_id', 'N/A')}"
    )

    if file_data.get("description"):
        print(f"description: {file_data.get('description')}")
    if file_data.get("hidden"):
        print(f"hidden: {file_data.get('hidden')}")
    if file_data.get("immutable"):
        print(f"immutable: {file_data.get('immutable')}")
    if file_data.get("archived"):
        print(f"archived: {file_data.get('archived')}")

def print_files_list(files_data, args):
    """
    Print table of files.

    Parameters
    ----------
    files_data : list
        List of file dictionaries
    args : argparse.Namespace
        Command line arguments, including the --json flag
    """
    if getattr(args, "json", False):
        json_printer(files_data)
        return
    elif getattr(args, "jsonl", False):
        jsonl_printer(files_data)
        return

    # Use the reusable dynamic table formatter
    dynamic_table_print(files_data, ["id", "type", "name"], ["ID", "Type", "File Name"])
    
def print_upload_result(response_data, response_status, file_name, file_size, data_provider_id):
    """
    Print the result of a file upload operation.

    Parameters
    ----------
    response_data : dict
        Response data from the server
    response_status : int
        HTTP status code
    file_name : str
        Name of the uploaded file
    file_size : int
        Size of the uploaded file in bytes
    data_provider_id : int
        ID of the data provider
    """
    print(
        f"Uploading {file_name} ({file_size} bytes) to data provider {data_provider_id}..."
    )

    if response_status == 200 or response_status == 201:
        print("File uploaded successfully!")
        if response_data.get("notice"):
            print(f"Server response: {response_data['notice']}")
    else:
        print(f"Upload failed with status: {response_status}")
        if response_data.get("notice"):
            print(f"Error: {response_data['notice']}")
        else:
            print(f"Response: {response_data}")

def print_move_copy_result(response_data, response_status, operation="move"):
    """
    Print the result of a file move or copy operation.

    Parameters
    ----------
    response_data : dict
        Response data from the server
    response_status : int
        HTTP status code
    operation : str
        Operation type ("move" or "copy")
    """
    if response_status == 200 or response_status == 201:
        # Show the message from the API response
        message = response_data.get("message", "").strip()
        if message:
            print(message)

        background_activity_id = response_data.get("background_activity_id")
        if background_activity_id:
            print(f"Background activity ID: {background_activity_id}")
        else:
            print(f"File {operation} initiated successfully")
    else:
        print(f"File {operation} failed with status: {response_status}")
