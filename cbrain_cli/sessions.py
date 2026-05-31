import datetime
import getpass
import json
import urllib.error

from cbrain_cli.cli_utils import api_post_form, api_send, api_token, cbrain_url
from cbrain_cli.config import CREDENTIALS_FILE, DEFAULT_BASE_URL


# MARK: Create Session.
def create_session(args):
    """
    Create a new CBRAIN session by logging in and saving credentials.

    Returns
    -------
    None
        A command is run via inputs from the user.
    """

    if CREDENTIALS_FILE.exists():
        print("Already logged in. Use 'cbrain logout' to logout.")
        return 1

    # Get user input.
    cbrain_url = input("Enter CBRAIN server base URL [default: localhost:3000]: ").strip()
    if not cbrain_url:
        cbrain_url = DEFAULT_BASE_URL

    username = input("Enter CBRAIN username: ").strip()
    if not username:
        print("Username is required")
        return 1

    password = getpass.getpass("Enter CBRAIN password: ")
    if not password:
        print("Password is required")
        return 1

    response_data = api_post_form(f"{cbrain_url}/session", {"login": username, "password": password})

    cbrain_api_token = response_data.get("cbrain_api_token")
    cbrain_user_id = response_data.get("user_id")

    if not cbrain_api_token:
        print("Login failed: No API token received")
        return 1

    credentials = {
        "cbrain_url": cbrain_url,
        "api_token": cbrain_api_token,
        "user_id": cbrain_user_id,
        "timestamp": datetime.datetime.now().isoformat(),
    }

    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f, indent=2)

    print(f"Connection successful, API token saved in {CREDENTIALS_FILE}")
    return 0


# MARK: Logout
def logout_session(args):
    """
    Logout from CBRAIN by deleting the session file.

    Returns
    -------
    None
        A command is run via inputs from the user.
    """

    if not cbrain_url or not api_token:
        print("Invalid credentials file. Removing local session.")
        CREDENTIALS_FILE.unlink()
        return 0

    try:
        _, status = api_send(f"{cbrain_url}/session", api_token, method="DELETE")
        if status == 200:
            print("Successfully logged out from CBRAIN server.")
        else:
            print("Logout failed")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("Session already expired on server.")
        else:
            print(f"Logout request failed: HTTP {e.code}")
    except urllib.error.URLError as e:
        print(f"Network error during logout: {e}")

    # Always remove local credentials file.
    CREDENTIALS_FILE.unlink()
    print(f"Local session removed from {CREDENTIALS_FILE}")
    return 0
