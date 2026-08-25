import datetime
import getpass
import urllib.error

from cbrain_cli import config as cbrain_config
from cbrain_cli.cli_utils import (
    CbrainClient,
    CliApiError,
    CliValidationError,
    session_name,
    session_specified,
)
from cbrain_cli.config import (
    ACTIVE_SESSION_KEY,
    DEFAULT_BASE_URL,
    get_named_sessions,
    is_flat_credentials,
    resolve_session_credentials,
)

# MARK: Switch Session


def switch_session(args):
    """Switch the default session used by bare commands."""
    target = getattr(args, "session_target", None)
    if not target:
        print("Usage: cbrain switch_session <session_name>")
        return 1

    all_creds = cbrain_config.load_credentials()
    if all_creds is None:
        print(f"Error: credentials file is corrupted ({cbrain_config.CREDENTIALS_FILE}).")
        return 1

    sessions = get_named_sessions(all_creds)
    if target not in sessions:
        available = ", ".join(sessions) or "(none)"
        print(f"Session '{target}' not found. Available sessions: {available}")
        return 1

    # Promote flat file to named map so _active_session can live alongside entries.
    if is_flat_credentials(all_creds):
        all_creds = {ACTIVE_SESSION_KEY: target, "default": sessions["default"]}
    else:
        all_creds[ACTIVE_SESSION_KEY] = target

    cbrain_config.save_credentials(all_creds)
    print(f"Switched to session '{target}'. All future commands will use this session.")
    return 0


# MARK: List Sessions


def list_sessions(args):
    """List all saved sessions, marking the currently active one with '*'."""
    all_creds = cbrain_config.load_credentials()
    if all_creds is None:
        print(f"Error: credentials file is corrupted ({cbrain_config.CREDENTIALS_FILE}).")
        return 1

    active = (
        all_creds.get(ACTIVE_SESSION_KEY, "default")
        if not is_flat_credentials(all_creds)
        else "default"
    )
    sessions = get_named_sessions(all_creds)

    if not sessions:
        print("No saved sessions. Use 'cbrain login' to create one.")
        return 0

    print(f"{'#':<4} {'SESSION':<20} {'USERNAME':<16} {'USER ID':<10} {'SERVER':<35} {'TIMESTAMP'}")
    print("-" * 90)
    for idx, (name, c) in enumerate(sessions.items(), start=1):
        marker = "*" if name == active else " "
        print(
            f"{marker}{idx:<3} {name:<20} {c.get('username', '(unknown)'):<16} "
            f"{c.get('user_id', 'N/A')!s:<10} {c.get('cbrain_url', 'N/A'):<35} "
            f"{c.get('timestamp', 'N/A')}"
        )

    print(f"\nActive session: {active}  (* = active)")
    return 0


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
    target_session = getattr(args, "session", None) or (
        session_name if session_specified else "default"
    )

    if cbrain_config.CREDENTIALS_FILE.exists():
        all_creds = cbrain_config.load_credentials()
        if all_creds:
            existing = resolve_session_credentials(
                all_creds, target_session if not is_flat_credentials(all_creds) else None
            )
            if existing.get("api_token") and existing.get("cbrain_url"):
                # File alone is not enough, probe server to detect expired tokens.
                try:
                    CbrainClient(
                        existing["cbrain_url"],
                        existing.get("api_token"),
                        existing.get("user_id"),
                    ).get("/session")
                except CliApiError as e:
                    if e.status == 401:
                        print("Saved session expired. Please log in again.")
                    elif e.status >= 500:
                        print(f"Server returned HTTP {e.status} during session check.")
                        print("The server may be temporarily unavailable. Try again later.")
                        return 1
                    else:
                        print(f"Server returned HTTP {e.status} during session check.")
                        print("Use 'cbrain logout' to reset local credentials.")
                        return 1
                except urllib.error.URLError:
                    print(f"Cannot reach CBRAIN server at {existing['cbrain_url']}.")
                    print("Check your connection. Use 'cbrain logout' to reset local credentials.")
                    return 1
                else:
                    label = f" to session '{target_session}'" if target_session != "default" else ""
                    print(f"Already logged in{label}. Use 'cbrain logout' to logout.")
                    return 1

    cbrain_url = (
        getattr(args, "server", None)
        or input("Enter CBRAIN server base URL [default: localhost:3000]: ").strip()
        or DEFAULT_BASE_URL
    )

    username = getattr(args, "username", None) or input("Enter CBRAIN username: ").strip()
    if not username:
        raise CliValidationError("Username is required", field="username")

    password = getattr(args, "password", None) or getpass.getpass("Enter CBRAIN password: ")
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
        "username": username,
        "timestamp": datetime.datetime.now().isoformat(),
    }

    # Named sessions → nested map; bare login keeps flat file (main-compatible).
    if target_session != "default" or session_specified:
        on_disk = cbrain_config.load_credentials() or {}
        if is_flat_credentials(on_disk):
            on_disk = {"default": {k: v for k, v in on_disk.items() if k != ACTIVE_SESSION_KEY}}
        on_disk[target_session] = credentials
        on_disk[ACTIVE_SESSION_KEY] = target_session
        cbrain_config.save_credentials(on_disk)
        print(
            f"Connection successful, API token saved in {cbrain_config.CREDENTIALS_FILE} "
            f"for session '{target_session}'"
        )
    else:
        cbrain_config.save_credentials(credentials)
        print(f"Connection successful, API token saved in {cbrain_config.CREDENTIALS_FILE}")
    return 0


# MARK: Logout


def logout_session(args):
    """
    Logout from CBRAIN.

    Without ``--session``: logout all sessions (or the single flat session).
    With ``--session <name>``: logout only that session.
    """
    if not cbrain_config.CREDENTIALS_FILE.exists():
        print("Not logged in. Use 'cbrain login' to login first.")
        return 0

    all_creds = cbrain_config.load_credentials()
    if all_creds is None:
        print("Invalid credentials file. Removing local session.")
        cbrain_config.CREDENTIALS_FILE.unlink(missing_ok=True)
        print(f"Local session removed from {cbrain_config.CREDENTIALS_FILE}")
        return 0

    sessions = get_named_sessions(all_creds)
    flat = is_flat_credentials(all_creds)

    if session_specified:
        sessions_to_logout = [session_name]
    else:
        sessions_to_logout = list(sessions)

    if not sessions_to_logout:
        print("Not logged in. Use 'cbrain login' to login first.")
        return 0

    for s_name in sessions_to_logout:
        creds = sessions.get(s_name, {})
        s_url, s_token = creds.get("cbrain_url"), creds.get("api_token")

        if not s_url or not s_token:
            if s_name in sessions:
                print(f"Invalid credentials for session '{s_name}'. Removing local session.")
                if flat:
                    cbrain_config.CREDENTIALS_FILE.unlink(missing_ok=True)
                    print(f"Local session removed from {cbrain_config.CREDENTIALS_FILE}")
                    return 0
                all_creds.pop(s_name, None)
            elif session_specified:
                print(f"Not logged in to session '{s_name}'.")
            elif len(sessions_to_logout) == 1:
                print("Not logged in. Use 'cbrain login' to login first.")
                if flat:
                    cbrain_config.CREDENTIALS_FILE.unlink(missing_ok=True)
                    print(f"Local session removed from {cbrain_config.CREDENTIALS_FILE}")
                    return 0
            continue

        display_name = creds.get("username", s_name)
        try:
            _, status = CbrainClient(s_url, s_token, creds.get("user_id")).send(
                "DELETE", "/session"
            )
            if status == 200:
                if flat or not session_specified and len(sessions_to_logout) == 1:
                    print("Successfully logged out from CBRAIN server.")
                else:
                    print(f"Successfully logged out from CBRAIN server as {display_name}.")
            else:
                print(f"Logout failed for session '{s_name}'." if not flat else "Logout failed")
        except CliApiError as e:
            if e.status == 401:
                print(
                    "Session already expired on server."
                    if flat
                    else f"Session '{s_name}' already expired on server."
                )
            else:
                print(
                    f"Logout request failed: HTTP {e.status}"
                    if flat
                    else f"Logout request failed for '{s_name}': HTTP {e.status}"
                )
        except urllib.error.URLError as e:
            print(
                f"Network error during logout: {e}"
                if flat
                else f"Network error during logout for '{s_name}': {e}"
            )

        if flat:
            if cbrain_config.CREDENTIALS_FILE.exists():
                cbrain_config.CREDENTIALS_FILE.unlink()
                print(f"Local session removed from {cbrain_config.CREDENTIALS_FILE}")
            return 0

        all_creds.pop(s_name, None)
        print(f"Local session '{s_name}' removed from {cbrain_config.CREDENTIALS_FILE}.")

    if not flat:
        remaining = get_named_sessions(all_creds)
        if not remaining:
            cbrain_config.CREDENTIALS_FILE.unlink(missing_ok=True)
        else:
            if all_creds.get(ACTIVE_SESSION_KEY) not in remaining:
                all_creds[ACTIVE_SESSION_KEY] = next(iter(remaining))
            cbrain_config.save_credentials(all_creds)
    return 0
