from cbrain_cli.cli_utils import (
    CbrainClient,
    json_printer,
)
from cbrain_cli.config import cli_session_not_found


def user_details(user_id):
    """
    Fetch user details from the CBRAIN API.

    Parameters
    ----------
    user_id : int
        CBRAIN user ID.

    Returns
    -------
    dict
        User data dictionary.
    """
    return CbrainClient.from_credentials().get(f"/users/{user_id}")


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
    missing = cli_session_not_found()
    if missing:
        msg = f"Session '{missing}' not found."
        if getattr(args, "json", False):
            json_printer({"error": msg, "logged_in": False})
        else:
            print(msg)
        return 1

    client = CbrainClient.from_credentials()

    # Check if we have credentials first
    if not client.user_id or not client.base_url or not client.token:
        if getattr(args, "json", False):
            json_printer({"error": "Credential file is missing", "logged_in": False})
        else:
            print("Credential file is missing. Use 'cbrain login' to login first.")
        return 1

    user_data = user_details(client.user_id)

    # Handle JSON output first
    if getattr(args, "json", False):
        output = {
            "login": user_data.get("login", ""),
            "full_name": user_data.get("full_name", ""),
            "server": client.base_url,
        }
        json_printer(output)
        return 0

    if version:
        # Verify token by making a session request.
        session_data = client.get("/session")

        # Verify local credentials match server response.
        remote_user_id = session_data.get("user_id")
        remote_token = session_data.get("cbrain_api_token")

        if str(remote_user_id) != str(client.user_id):
            print(f"WARNING: User ID mismatch - Local: {client.user_id}, Remote: {remote_user_id}")

        if remote_token != client.token:
            print("WARNING: Token mismatch - tokens don't match")

    login = user_data.get("login", "")
    full_name = user_data.get("full_name", "")
    print(f"Current user: {login} ({full_name}) on server {client.base_url}")
