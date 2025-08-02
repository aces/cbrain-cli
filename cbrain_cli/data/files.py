import json
import mimetypes
import os
import urllib.error
import urllib.parse
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url
from cbrain_cli.config import auth_headers
from cbrain_cli.data.background_activitites import show_background_activity


def show_file(args):
    """
    Get detailed information about a specific file from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the file argument with file_id

    Returns
    -------
    dict or None
        Dictionary containing file details if successful, None otherwise
    """
    # Get the file ID from the --file argument.
    file_id = getattr(args, "file", None)
    if not file_id:
        print("Error: File ID is required")
        return None

    userfile_endpoint = f"{cbrain_url}/userfiles/{file_id}"
    headers = auth_headers(api_token)

    request = urllib.request.Request(
        userfile_endpoint, data=None, headers=headers, method="GET"
    )

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        file_data = json.loads(data)

    return file_data


def upload_file(args):
    """
    Upload a file to CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments including data_provider, file_type, file_path, and group_id

    Returns
    -------
    tuple
        (response_data, response_status, file_name, file_size) or None if error
    """
    # Check if file exists.
    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}")
        return None

    # Handle the case where group_id might be passed with hyphens.
    if hasattr(args, "group_id") and args.group_id:
        group_id = args.group_id

    # Get file information.
    file_name = os.path.basename(args.file_path)
    file_size = os.path.getsize(args.file_path)

    # Determine MIME type.
    mime_type, _ = mimetypes.guess_type(args.file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    # Create multipart form data.
    boundary = "----formdata-cbrain-cli"

    # Build the multipart body.
    body_parts = []

    # Add data_provider_id field.
    body_parts.append(f"--{boundary}")
    body_parts.append('Content-Disposition: form-data; name="data_provider_id"')
    body_parts.append("")
    body_parts.append(str(args.data_provider))

    # Add userfile[group_id] field.
    body_parts.append(f"--{boundary}")
    body_parts.append('Content-Disposition: form-data; name="userfile[group_id]"')
    body_parts.append("")
    body_parts.append(str(group_id))

    # Add file_type field.
    body_parts.append(f"--{boundary}")
    body_parts.append('Content-Disposition: form-data; name="file_type"')
    body_parts.append("")
    body_parts.append(args.file_type)

    # Add file data.
    body_parts.append(f"--{boundary}")
    body_parts.append(
        f'Content-Disposition: form-data; name="upload_file"; filename="{file_name}"'
    )
    body_parts.append(f"Content-Type: {mime_type}")
    body_parts.append("")

    # Join the text parts.
    body_text = "\r\n".join(body_parts) + "\r\n"

    # Read file content.
    with open(args.file_path, "rb") as f:
        file_content = f.read()

    # Complete the multipart body.
    body_end = f"\r\n--{boundary}--\r\n"

    body = body_text.encode("utf-8") + file_content + body_end.encode("utf-8")

    # Prepare headers.
    headers = auth_headers(api_token)
    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    headers["Content-Length"] = str(len(body))

    # Create the request.
    upload_endpoint = f"{cbrain_url}/userfiles"
    request = urllib.request.Request(
        upload_endpoint, data=body, headers=headers, method="POST"
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            response_data = json.loads(data)
            return response_data, response.status, file_name, file_size, args.data_provider

    except urllib.error.HTTPError as e:
        # Handle HTTP errors (like 422) that contain JSON responses.
        try:
            error_data = e.read().decode("utf-8")
            error_response = json.loads(error_data)
            return error_response, e.code, file_name, file_size, args.data_provider
        except (json.JSONDecodeError, UnicodeDecodeError):
            error_data = e.read().decode("utf-8", errors="ignore")
            return {"error": error_data}, e.code, file_name, file_size, args.data_provider


def copy_file(args):
    """
    Copy files to a different data provider.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including file-id (list) and dp-id

    Returns
    -------
    tuple
        (response_data, response_status) or None if error
    """
    # Get the file IDs and destination data provider ID
    file_ids = getattr(args, "file_id", None)
    dest_provider_id = getattr(args, "dp_id", None) or getattr(
        args, "data_provider_id_for_mv_cp", None
    )

    if not file_ids:
        print("Error: File ID(s) are required")
        return None

    if not dest_provider_id:
        print("Error: Destination data provider ID is required")
        return None

    change_provider_endpoint = f"{cbrain_url}/userfiles/change_provider"
    headers = auth_headers(api_token)
    headers["Content-Type"] = "application/json"

    payload = {
        "file_ids": file_ids,
        "data_provider_id_for_mv_cp": dest_provider_id,
        "copy": "",  # Empty string indicates copy operation
    }

    json_data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        change_provider_endpoint, data=json_data, headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            response_data = json.loads(data)
            return response_data, response.status

    except urllib.error.HTTPError as e:
        try:
            error_data = e.read().decode("utf-8")
            error_response = json.loads(error_data)
            return error_response, e.code
        except (json.JSONDecodeError, UnicodeDecodeError):
            error_data = e.read().decode("utf-8", errors="ignore")
            return {"error": error_data}, e.code


def move_file(args):
    """
    Move files to a different data provider.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including file-id (list) and dp-id

    Returns
    -------
    tuple
        (response_data, response_status) or None if error
    """
    # Get the file IDs and destination data provider ID
    file_ids = getattr(args, "file_id", None)
    dest_provider_id = getattr(args, "dp_id", None) or getattr(
        args, "data_provider_id_for_mv_cp", None
    )

    if not file_ids:
        print("Error: File ID(s) are required")
        return None

    if not dest_provider_id:
        print("Error: Destination data provider ID is required")
        return None

    change_provider_endpoint = f"{cbrain_url}/userfiles/change_provider"
    headers = auth_headers(api_token)
    headers["Content-Type"] = "application/json"

    # Prepare the payload for move operation
    payload = {
        "file_ids": file_ids,
        "data_provider_id_for_mv_cp": dest_provider_id,
        "move": "",  # "move" key indicates move operation
    }

    json_data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        change_provider_endpoint, data=json_data, headers=headers, method="POST"
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            response_data = json.loads(data)
            return response_data, response.status

    except urllib.error.HTTPError as e:
        try:
            error_data = e.read().decode("utf-8")
            error_response = json.loads(error_data)
            return error_response, e.code
        except (json.JSONDecodeError, UnicodeDecodeError):
            error_data = e.read().decode("utf-8", errors="ignore")
            return {"error": error_data}, e.code


def list_files(args):
    """
    Get list of all files from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag, filter options, and pagination

    Returns
    -------
    tuple
        (files_data, page) or None if error
    """
    # Validate per_page parameter
    per_page = getattr(args, "per_page", 25)
    if per_page < 5 or per_page > 1000:
        print("Error: per-page must be between 5 and 1000")
        return None

    # Build query parameters for filtering
    query_params = {}

    # Add filter parameters if provided
    if hasattr(args, "group_id") and args.group_id is not None:
        query_params["group_id"] = str(args.group_id)

    if hasattr(args, "dp_id") and args.dp_id is not None:
        query_params["data_provider_id"] = str(args.dp_id)

    if hasattr(args, "user_id") and args.user_id is not None:
        query_params["user_id"] = str(args.user_id)

    if hasattr(args, "parent_id") and args.parent_id is not None:
        query_params["parent_id"] = str(args.parent_id)

    if hasattr(args, "file_type") and args.file_type is not None:
        query_params["type"] = args.file_type

    page = getattr(args, "page", 1)
    if page < 1:
        print("Error: page must be 1 or greater")
        return None
        
    query_params["page"] = str(page)
    query_params["per_page"] = str(per_page)
    
    userfiles_endpoint = f"{cbrain_url}/userfiles"
    query_string = urllib.parse.urlencode(query_params)
    userfiles_endpoint = f"{userfiles_endpoint}?{query_string}"
    
    headers = auth_headers(api_token)
    request = urllib.request.Request(
        userfiles_endpoint, data=None, headers=headers, method="GET"
    )
    
    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        files_data = json.loads(data)

    return files_data, page


def delete_file(args):
    """
    Delete a file from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the file_id argument

    Returns
    -------
    tuple
        (response_data, response_status) or None if error
    """
    # Get the file ID from the argument.
    file_id = getattr(args, "file_id", None)
    if not file_id:
        print("Error: File ID is required")
        return None

    delete_endpoint = f"{cbrain_url}/userfiles/delete_files"
    headers = auth_headers(api_token)
    headers["Content-Type"] = "application/json"

    payload = {
        "file_ids": [str(file_id)]
    }

    json_data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        delete_endpoint, data=json_data, headers=headers, method="DELETE"
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            try:
                response_data = json.loads(data)
            except json.JSONDecodeError:
                response_data = data
            return response_data 

    except urllib.error.HTTPError as e:
        try:
            error_data = e.read().decode("utf-8")
            error_response = json.loads(error_data)
            return error_response, e.code
        except (json.JSONDecodeError, UnicodeDecodeError):
            error_data = e.read().decode("utf-8", errors="ignore")
            return {"error": error_data}, e.code
