import datetime
import getpass
import urllib.error

from cbrain_cli import config as cbrain_config
from cbrain_cli.cli_utils import (
    CbrainClient,
    CliApiError,
    CliValidationError,
)
from cbrain_cli.config import DEFAULT_BASE_URL


# MARK: Create Session.
def create_session(args):
    """
    Create a new CBRAIN session by logging in and saving credentials.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments (unused; login is interactive).

    Returns
    -------
    int
        Exit code (0 on success, 1 on failure).
    """

    if cbrain_config.CREDENTIALS_FILE.exists():
        creds = cbrain_config.load_credentials()
        if creds and creds.get("api_token") and creds.get("cbrain_url"):
            # File alone is not enough, probe server to detect expired tokens.
            try:
                CbrainClient.from_credentials().get("/session")
            except CliApiError as e:
                if e.status == 401:
                    print("Saved session expired. Please log in again.")
                else:
                    print("Already logged in. Use 'cbrain logout' to logout.")
                    return 1
            except urllib.error.URLError:
                print("Already logged in. Use 'cbrain logout' to logout.")
                return 1
            else:
                print("Already logged in. Use 'cbrain logout' to logout.")
                return 1

    # Get user input.
    cbrain_url = input("Enter CBRAIN server base URL [default: localhost:3000]: ").strip()
    if not cbrain_url:
        cbrain_url = DEFAULT_BASE_URL

    username = input("Enter CBRAIN username: ").strip()
    if not username:
        raise CliValidationError("Username is required", field="username")

    password = getpass.getpass("Enter CBRAIN password: ")
    if not password:
        raise CliValidationError("Password is required", field="password")

    response_data = CbrainClient(cbrain_url).post_form(
        "/session", {"login": username, "password": password}
    )

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

    cbrain_config.save_credentials(credentials)

    print(f"Connection successful, API token saved in {cbrain_config.CREDENTIALS_FILE}")
    return 0


# MARK: Logout
def logout_session(args):
    """
    Logout from CBRAIN by deleting the session file.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments (unused).

    Returns
    -------
    int
        Exit code (0 on success).
    """

    if not cbrain_config.CREDENTIALS_FILE.exists():
        print("Not logged in. Use 'cbrain login' to login first.")
        return 0

    credentials = cbrain_config.load_credentials()
    if credentials is None:
        print("Invalid credentials file. Removing local session.")
        cbrain_config.CREDENTIALS_FILE.unlink(missing_ok=True)
        print(f"Local session removed from {cbrain_config.CREDENTIALS_FILE}")
        return 0

    cbrain_url = credentials.get("cbrain_url")
    api_token = credentials.get("api_token")
    if not cbrain_url or not api_token:
        print("Invalid credentials file. Removing local session.")
        cbrain_config.CREDENTIALS_FILE.unlink(missing_ok=True)
        print(f"Local session removed from {cbrain_config.CREDENTIALS_FILE}")
        return 0

    try:
        _, status = CbrainClient.from_credentials().send("DELETE", "/session")
        if status == 200:
            print("Successfully logged out from CBRAIN server.")
        else:
            print("Logout failed")
    except CliApiError as e:
        if e.status == 401:
            print("Session already expired on server.")
        else:
            print(f"Logout request failed: HTTP {e.status}")
    except urllib.error.URLError as e:
        print(f"Network error during logout: {e}")

    if cbrain_config.CREDENTIALS_FILE.exists():
        cbrain_config.CREDENTIALS_FILE.unlink()
        print(f"Local session removed from {cbrain_config.CREDENTIALS_FILE}")
    return 0
