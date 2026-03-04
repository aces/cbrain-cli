import datetime
import getpass
import json
import urllib.error
import urllib.parse
import urllib.request

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
        A command is run via inputs from the user.
    """
    from cbrain_cli.cli_utils import all_credentials, api_token, cbrain_url, session_name

    if cbrain_url is not None and api_token is not None:
        print(f"Already logged in to session '{session_name}'. Use 'cbrain logout' to logout.")
        return 1

    # Get user input.
    cbrain_url_input = getattr(args, "server", None) or input(
        "Enter CBRAIN server base URL [default: localhost:3000]: "
    ).strip()
    if not cbrain_url_input:
        cbrain_url_input = DEFAULT_BASE_URL

    username = getattr(args, "username", None) or input("Enter CBRAIN username: ").strip()
    if not username:
        print("Username is required")
        return 1

    password = getattr(args, "password", None) or getpass.getpass("Enter CBRAIN password: ")
    if not password:
        print("Password is required")
        return 1

    # Prepare the login request.
    login_endpoint = f"{cbrain_url_input}/session"

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
            "cbrain_url": cbrain_url_input,
            "api_token": cbrain_api_token,
            "user_id": cbrain_user_id,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        # Save credentials to file.
        all_credentials[session_name] = credentials
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(all_credentials, f, indent=2)

        print(
            f"Connection successful, API token saved in {CREDENTIALS_FILE} "
            f"for session '{session_name}'"
        )
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
    from cbrain_cli.cli_utils import all_credentials, session_name, session_specified

    if not session_specified and len(all_credentials) > 0:
        sessions_to_logout = list(all_credentials.keys())
    else:
        sessions_to_logout = [session_name]

    if not sessions_to_logout:
        print("No active sessions to logout.")
        return 0

    for s_name in sessions_to_logout:
        creds = all_credentials.get(s_name, {})
        s_url = creds.get("cbrain_url")
        s_token = creds.get("api_token")
        s_uid = creds.get("user_id")

        if not s_url or not s_token:
            if s_name in all_credentials:
                print(f"Invalid credentials for session '{s_name}'. Removing local session.")
                del all_credentials[s_name]
            else:
                if session_specified:
                    print(f"Not logged in to session '{s_name}'.")
                elif len(sessions_to_logout) == 1 and s_name == "default":
                    print("Not logged in. Use 'cbrain login' to login first.")
            continue

        # Try to fetch username for a nicer logout message
        username = s_name
        try:
            req = urllib.request.Request(
                f"{s_url}/users/{s_uid}", headers=auth_headers(s_token), method="GET"
            )
            with urllib.request.urlopen(req) as response:
                user_data = json.loads(response.read().decode("utf-8"))
                username = user_data.get("login", s_name)
        except Exception:
            pass

        # Prepare logout request.
        logout_endpoint = f"{s_url}/session"

        # Create the DELETE request.
        request = urllib.request.Request(
            logout_endpoint,
            data=None,  # No payload for DELETE
            headers=auth_headers(s_token),
            method="DELETE",
        )

        # Make the request to logout from server.
        try:
            with urllib.request.urlopen(request) as response:
                if response.status == 200:
                    print(f"Successfully logged out from CBRAIN server as {username}.")
                else:
                    print(f"Logout failed for session '{s_name}'.")
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print(f"Session '{s_name}' already expired on server.")
            else:
                print(f"Logout request failed for '{s_name}': HTTP {e.code}")
        except urllib.error.URLError as e:
            print(f"Network error during logout for '{s_name}': {e}")

        # Always remove local credentials for this session.
        if s_name in all_credentials:
            del all_credentials[s_name]
        print(f"Local session '{s_name}' removed from {CREDENTIALS_FILE}")

    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(all_credentials, f, indent=2)

    return 0
