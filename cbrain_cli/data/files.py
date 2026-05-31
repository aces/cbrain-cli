import json
import mimetypes
import os
import urllib.request

from cbrain_cli.cli_utils import api_get, api_send, api_token, cbrain_url, pagination
from cbrain_cli.config import auth_headers


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
    return api_get(f"{cbrain_url}/userfiles/{file_id}", api_token)


def upload_file(args):
    """
    Upload a file to CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments including data_provider, file_path, and group_id

    Returns
    -------
    tuple
        (response_data, response_status, file_name, file_size) or None if error
    """
    # Check if file exists.
    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}")
        return None

    if args.group_id is None:
        print("Error: Group ID is required")
        return None

    file_name = os.path.basename(args.file_path)
    file_size = os.path.getsize(args.file_path)

    mime_type, _ = mimetypes.guess_type(args.file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    boundary = "----formdata-cbrain-cli"
    body_parts = [
        f"--{boundary}",
        'Content-Disposition: form-data; name="data_provider_id"',
        "",
        str(args.data_provider),
        f"--{boundary}",
        'Content-Disposition: form-data; name="userfile[group_id]"',
        "",
        str(args.group_id),
        f"--{boundary}",
        f'Content-Disposition: form-data; name="upload_file"; filename="{file_name}"',
        f"Content-Type: {mime_type}",
        "",
    ]

    body_text = "\r\n".join(body_parts) + "\r\n"
    with open(args.file_path, "rb") as f:
        file_content = f.read()

    body = body_text.encode("utf-8") + file_content + f"\r\n--{boundary}--\r\n".encode()

    headers = auth_headers(api_token)
    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    headers["Content-Length"] = str(len(body))

    request = urllib.request.Request(
        f"{cbrain_url}/userfiles", data=body, headers=headers, method="POST"
    )
    with urllib.request.urlopen(request) as response:
        response_data = json.loads(response.read().decode("utf-8"))
        return response_data, response.status, file_name, file_size, args.data_provider


def _change_provider(args, operation):
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
    payload = {
        "file_ids": file_ids,
        "data_provider_id_for_mv_cp": dest_provider_id,
        operation: "",
    }
    return api_send(f"{cbrain_url}/userfiles/change_provider", api_token, payload=payload)


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
    return _change_provider(args, "copy")


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
    return _change_provider(args, "move")


def list_files(args):
    """
    Get list of all files from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the --json flag, filter options, and pagination

    Returns
    -------
    list or None
        List of file dictionaries, or None if error
    """
    params = {}
    for attr, key in [
        ("group_id", "group_id"),
        ("dp_id", "data_provider_id"),
        ("user_id", "user_id"),
        ("parent_id", "parent_id"),
        ("file_type", "type"),
    ]:
        val = getattr(args, attr, None)
        if val is not None:
            params[key] = str(val)

    params = pagination(args, params)
    if params is None:
        return None
    return api_get(f"{cbrain_url}/userfiles", api_token, params)


def delete_file(args):
    """
    Delete a file from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the file_id argument

    Returns
    -------
    dict or None
        Response data, or None if error
    """
    file_id = getattr(args, "file_id", None)
    if not file_id:
        print("Error: File ID is required")
        return None
    data, _ = api_send(
        f"{cbrain_url}/userfiles/delete_files",
        api_token,
        method="DELETE",
        payload={"file_ids": [str(file_id)]},
    )
    return data
