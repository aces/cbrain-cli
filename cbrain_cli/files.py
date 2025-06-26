import json
import mimetypes
import os
import urllib.error
import urllib.parse
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url
from cbrain_cli.config import auth_headers


def show_file(args):
    """
    Show detailed information about a specific file from CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the file argument with file_id
    """

    # Get the file ID from the --file argument.
    file_id = getattr(args, "file", None)
    if not file_id:
        print("Error: File ID is required")
        return 1

    # Prepare the API request.
    userfile_endpoint = f"{cbrain_url}/userfiles/{file_id}"
    headers = auth_headers(api_token)

    # Create the request.
    request = urllib.request.Request(
        userfile_endpoint, data=None, headers=headers, method="GET"
    )

    # Make the request.
    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        file_data = json.loads(data)

    # Output the file details.
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

    # Optional fields.
    if file_data.get("description"):
        print(f"description: {file_data.get('description')}")
    if file_data.get("hidden"):
        print(f"hidden: {file_data.get('hidden')}")
    if file_data.get("immutable"):
        print(f"immutable: {file_data.get('immutable')}")
    if file_data.get("archived"):
        print(f"archived: {file_data.get('archived')}")

    return 0


def upload_file(args):
    """
    Upload a file to CBRAIN.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments including data_provider, file_type, file_path, and group_id
    """

    # Check if file exists.
    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}")
        return 1

    # Handle the case where group_id might be passed with hyphens.
    if hasattr(args, "group_id") and args.group_id:
        group_id = args.group_id

    # Prepare the API request.
    upload_endpoint = f"{cbrain_url}/userfiles"

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

    # Add userfile[type] field.
    body_parts.append(f"--{boundary}")
    body_parts.append('Content-Disposition: form-data; name="userfile[type]"')
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

    # Combine all parts.
    body = body_text.encode("utf-8") + file_content + body_end.encode("utf-8")

    # Prepare headers.
    headers = auth_headers(api_token)
    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    headers["Content-Length"] = str(len(body))

    # Create the request.
    request = urllib.request.Request(
        upload_endpoint, data=body, headers=headers, method="POST"
    )

    print(
        f"Uploading {file_name} ({file_size} bytes) to data provider {args.data_provider}..."
    )

    # Make the request.
    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            response_data = json.loads(data)

            if response.status == 200 or response.status == 201:
                print("File uploaded successfully!")
                if response_data.get("notice"):
                    print(f"Server response: {response_data['notice']}")
                return 0
            else:
                print(f"Upload failed with status: {response.status}")
                if response_data.get("notice"):
                    print(f"Error: {response_data['notice']}")
                else:
                    print(f"Response: {data}")
                return 1
    except urllib.error.HTTPError as e:
        # Handle HTTP errors (like 422) that contain JSON responses.
        try:
            error_data = e.read().decode("utf-8")
            error_response = json.loads(error_data)
            print(f"Upload failed with status: {e.code}")
            if error_response.get("notice"):
                print(f"Error: {error_response['notice']}")
            else:
                print(f"Response: {error_data}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"Upload failed with status: {e.code}")
            print(f"Response: {e.read().decode('utf-8', errors='ignore')}")
        return 1
