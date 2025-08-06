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