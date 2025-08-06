import datetime
import getpass
import json
import urllib.error
import urllib.parse
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url
from cbrain_cli.config import (
    CREDENTIALS_FILE,
    DEFAULT_BASE_URL,
    DEFAULT_HEADERS,
    auth_headers,
)


# MARK: Create Session.
def create_session(args):
    """
    Create a new CBRAIN session by logging in and saving credentials.

    Returns
    -------
    None
        A command is ran via inputs from the user.
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

    # Prepare the login request.
    login_endpoint = f"{cbrain_url}/session"

    # Prepare form data.
    form_data = {"login": username, "password": password}

    # Encode the form data.
    encoded_data = urllib.parse.urlencode(form_data).encode("utf-8")

    # Create the request.
    request = urllib.request.Request(
        login_endpoint, data=encoded_data, headers=DEFAULT_HEADERS, method="POST"
    )

    # Make the request.
    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        response_data = json.loads(data)

        # Extract the API token from response.
        cbrain_api_token = response_data.get("cbrain_api_token")
        cbrain_user_id = response_data.get("user_id")

        if not cbrain_api_token:
            print("Login failed: No API token received")
            return 1

        # Prepare credentials data.
        credentials = {
            "cbrain_url": cbrain_url,
            "api_token": cbrain_api_token,
            "user_id": cbrain_user_id,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        # Save credentials to file.
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
        A command is ran via inputs from the user.
    """

    if not cbrain_url or not api_token:
        print("Invalid credentials file. Removing local session.")
        CREDENTIALS_FILE.unlink()
        return 0

    # Prepare logout request.
    logout_endpoint = f"{cbrain_url}/session"

    # Create headers with authorization.
    headers = auth_headers(api_token)

    # Create the DELETE request.
    request = urllib.request.Request(
        logout_endpoint,
        data=None,  # No payload for DELETE
        headers=headers,
        method="DELETE",
    )

    # Make the request to logout from server.
    with urllib.request.urlopen(request) as response:
        if response.status == 200:
            print("Successfully logged out from CBRAIN server.")
        else:
            print("Logout failed")

    # Always remove local credentials file.
    CREDENTIALS_FILE.unlink()
    print(f"Local session removed from {CREDENTIALS_FILE}")
    return 0
