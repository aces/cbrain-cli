import datetime
import functools
import json
import urllib.error
# import importlib.metadata

from cbrain_cli.config import CREDENTIALS_FILE

try:
    # MARK: Credentials.
    with open(CREDENTIALS_FILE, "r") as f:
        credentials = json.load(f)

    # Get credentials.
    cbrain_url = credentials.get("cbrain_url")
    api_token = credentials.get("api_token")
    user_id = credentials.get("user_id")
    cbrain_timestamp = credentials.get("timestamp")
except FileNotFoundError:
    cbrain_url = None
    api_token = None
    user_id = None
    cbrain_timestamp = None


def is_authenticated():
    """
    Check if the user is authenticated.
    """

    if cbrain_timestamp:
        timestamp_obj = datetime.datetime.fromisoformat(cbrain_timestamp)
        if datetime.datetime.now() - timestamp_obj > datetime.timedelta(days=1):
            print("Session expired. Please log in again using 'cbrain login'.")
            CREDENTIALS_FILE.unlink()
            return False
    # Check if user is logged in.
    if not api_token or not cbrain_url or not user_id:
        print("Not logged in. Use 'cbrain login' to login first.")
        return False
    return True


def handle_connection_error(error):
    """
    Handle connection errors with informative messages including server URL.

    Parameters
    ----------
    error : Exception
        The connection error that occurred

    Returns
    -------
    None
        Prints appropriate error messages
    """
    if isinstance(error, urllib.error.URLError):
        if "Connection refused" in str(error):
            print(f"Error: Cannot connect to CBRAIN server at {cbrain_url}")
            print("Please check if the CBRAIN server is running and accessible.")
        else:
            print(f"Connection failed: {error.reason}")
    elif isinstance(error, urllib.error.HTTPError):
        print(f"Request failed: HTTP {error.code} - {error.reason}")
        if error.code == 401:
            print("Invalid username or password")
        elif error.code == 404:
            print("Resource not found")
        elif error.code == 500:
            print("Internal server error")
    else:
        print(f"Connection error: {str(error)}")


def handle_errors(func):
    """
    Decorator to handle common errors for all CLI commands.

    Returns
    -------
    None
        A command is ran via inputs from the user.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except urllib.error.HTTPError as e:
            handle_connection_error(e)
            return 1
        except urllib.error.URLError as e:
            handle_connection_error(e)
            return 1
        except json.JSONDecodeError:
            print("Failed: Invalid response from server")
            return 1
        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return 1
        except Exception as e:
            print(f"Operation failed: {str(e)}")
            return 1

    return wrapper

def version_info(args):
    """
    Display the CLI version information.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    print("cbrain cli client version 1.0")
    # try:
    #     cbrain_cli_version = importlib.metadata.version('cbrain-cli') 
    #     print(f"cbrain cli client version {cbrain_cli_version}")
    #     return 0
    # except importlib.metadata.PackageNotFoundError:
    #     print("Warning: Could not determine version. Package may not be installed properly.")
    #     return 1

def json_printer(data):
    """
    Print data in JSON format.
    """
    print(json.dumps(data, indent=2))
    return 0

def jsonl_printer(data):
    """
    Print data in JSONL format.
    Each object is printed as a single line of JSON with no indentation.
    For lists, each object is separated by newlines with no commas or enclosing brackets.
    """
    if isinstance(data, list):
        for item in data:
            print(json.dumps(item, separators=(',', ':')))
    else:
        print(json.dumps(data, separators=(',', ':')))
    return 0

def pagination(args,query_params):
    """
    Validate the per_page parameter.
    """
    per_page = getattr(args, "per_page", 25)
    if per_page < 5 or per_page > 1000:
        print("Error: per-page must be between 5 and 1000")
        return None
    
    page = getattr(args, "page", 1)
    if page < 1:
        print("Error: page must be 1 or greater")
        return None
        
    query_params["page"] = str(page)
    query_params["per_page"] = str(per_page)

    return query_params

def dynamic_table_print(data, columns, headers=None):
    """
    Print data in a dynamically-sized table format with proper column alignment.
    
    Parameters
    ----------
    data : list of dict
        List of dictionaries containing the data to display
    columns : list of str
        List of column keys to extract from each data dictionary
    headers : list of str, optional
        List of header names. If None, uses the column keys as headers
        
    Returns
    -------
    None
        Prints the formatted table to stdout
        
    Examples
    --------
    >>> data = [
    ...     {"id": 1234567, "type": "ReconAllCrossSectionalOutput", "name": "file1.txt"},
    ...     {"id": 5, "type": "SingleFile", "name": "demo.txt"}
    ... ]
    >>> dynamic_table_print(data, ["id", "type", "name"], ["ID", "Type", "File Name"])
    """
    if not data:
        print("No data found.")
        return
        
    # Use column keys as headers if none provided
    if headers is None:
        headers = columns
        
    if len(headers) != len(columns):
        raise ValueError("Number of headers must match number of columns")
    
    # Calculate dynamic column widths based on actual data and headers
    column_widths = []
    for i, (column, header) in enumerate(zip(columns, headers)):
        # Get max width needed for this column (data + header)
        max_data_width = max(len(str(item.get(column, ""))) for item in data)
        max_width = max(max_data_width, len(str(header)))
        column_widths.append(max_width)
    
    # Print header with dynamic spacing
    header_parts = []
    separator_parts = []
    for i, (header, width) in enumerate(zip(headers, column_widths)):
        if i == len(headers) - 1:  # Last column doesn't need right padding
            header_parts.append(str(header))
            separator_parts.append("-" * len(str(header)))
        else:
            header_parts.append(f"{header:<{width}}")
            separator_parts.append("-" * width)
    
    print(" ".join(header_parts))
    print(" ".join(separator_parts))
    
    # Print each row with dynamic spacing
    for item in data:
        row_parts = []
        for i, (column, width) in enumerate(zip(columns, column_widths)):
            value = str(item.get(column, ""))
            if i == len(columns) - 1:  # Last column doesn't need right padding
                row_parts.append(value)
            else:
                row_parts.append(f"{value:<{width}}")
        print(" ".join(row_parts))