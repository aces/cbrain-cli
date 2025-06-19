import json
import urllib.error
import functools

from cbrain_cli.config import CREDENTIALS_FILE

try:
    # MARK: Credentials.
    with open(CREDENTIALS_FILE, 'r') as f:
        credentials = json.load(f) 

    # Get credentials.
    cbrain_url = credentials.get('cbrain_url')
    api_token = credentials.get('api_token')
    user_id = credentials.get('user_id')
except FileNotFoundError:
    cbrain_url = None
    api_token = None
    user_id = None

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
            print(f"Request failed: HTTP {e.code} - {e.reason}")
            if e.code == 401:
                print("Invalid username or password")
            return 1
        except urllib.error.URLError as e:
            print(f"Connection failed: {e.reason}")
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

