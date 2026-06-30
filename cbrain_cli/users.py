import json
import urllib.error
import urllib.request

from cbrain_cli.cli_utils import (
    api_token,
    cbrain_url,
    handle_connection_error,
    json_printer,
    user_id,
)
from cbrain_cli.config import auth_headers


def user_details(user_id):
    """
    Fetch user details from the CBRAIN API.

    Parameters
    ----------
    user_id : int
        CBRAIN user ID.

    Returns
    -------
    dict or None
        User data dictionary, or None if the request fails.
    """
    user_endpoint = f"{cbrain_url}/users/{user_id}"

    user_request = urllib.request.Request(
        user_endpoint, headers=auth_headers(api_token), method="GET"
    )

    try:
        with urllib.request.urlopen(user_request) as response:
            user_data = json.loads(response.read().decode("utf-8"))
            return user_data

    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        handle_connection_error(e)
        return None
    except Exception as e:
        print(f"Error getting user details: {e}")
        return None


# MARK: Whoami
def whoami_user(args):
    """
    Display current user information by fetching details from the server.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments (json, version flags).

    Returns
    -------
    int or None
        Exit code on credential or API failure; otherwise None after printing.
    """
    version = getattr(args, "version", False)

    # Check if we have credentials first
    if user_id is None or cbrain_url is None or api_token is None:
        if getattr(args, "json", False):
            json_printer({"error": "Credential file is missing", "logged_in": False})
        else:
            print("Credential file is missing. Use 'cbrain login' to login first.")
        return 1

    user_data = user_details(user_id)

    # Check if user_data is valid before proceeding
    if user_data is None:
        return 1

    # Handle JSON output first
    if getattr(args, "json", False):
        output = {
            "login": user_data["login"],
            "full_name": user_data["full_name"],
            "server": cbrain_url,
        }
        json_printer(output)
        return 0

    if version:
        # Verify token by making a session request.
        session_endpoint = f"{cbrain_url}/session"

        session_request = urllib.request.Request(
            session_endpoint, headers=auth_headers(api_token), method="GET"
        )

        try:
            with urllib.request.urlopen(session_request) as response:
                session_data = json.loads(response.read().decode("utf-8"))

                # Verify local credentials match server response.
                remote_user_id = session_data.get("user_id")
                remote_token = session_data.get("cbrain_api_token")

                if str(remote_user_id) != str(user_id):
                    print(f"WARNING: User ID mismatch - Local: {user_id}, Remote: {remote_user_id}")

                if remote_token != api_token:
                    print("WARNING: Token mismatch - tokens don't match")

        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            handle_connection_error(e)
            return 1
        except Exception as e:
            print(f"Error verifying session: {e}")
            return 1

    print(f"Current user: {user_data['login']} ({user_data['full_name']}) on server {cbrain_url}")
