import datetime
import getpass
import json
import urllib.error
import urllib.parse
import urllib.request

from cbrain_cli.config import (
    ACTIVE_SESSION_KEY,
    CREDENTIALS_FILE,
    DEFAULT_BASE_URL,
    DEFAULT_HEADERS,
    auth_headers,
)

## MARK: Internal helpers

def load_credentials() -> dict:
    """Load cbrain.json; return {} if missing, raise on corrupt JSON."""
    try:
        with open(CREDENTIALS_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_credentials(data: dict) -> None:
    """Merge *data* into cbrain.json, preserving metadata keys (e.g. _active_session)."""
    on_disk = load_credentials()          # always re-read so we don't lose metadata
    on_disk.update(data)                 # overlay the caller's session changes
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(on_disk, f, indent=2)


def get_sessions(all_creds: dict) -> dict:
    """Return only genuine session entries (skip the metadata key)."""
    return {name: creds for name, creds in all_creds.items() if name != ACTIVE_SESSION_KEY}


# MARK: Switch Session

def switch_session(args):
    """Switch the default session used by bare commands."""
    target = getattr(args, "session_target", None)
    if not target:
        print("Usage: cbrain switch_session <session_name>")
        return 1

    try:
        all_creds = load_credentials()
    except json.JSONDecodeError:
        print(f"Error: credentials file is corrupted ({CREDENTIALS_FILE}).")
        return 1

    sessions = get_sessions(all_creds)
    if target not in sessions:
        available = ", ".join(sessions) or "(none)"
        print(f"Session '{target}' not found. Available sessions: {available}")
        return 1

    all_creds[ACTIVE_SESSION_KEY] = target
    save_credentials(all_creds)
    print(f"Switched to session '{target}'. All future commands will use this session.")
    return 0


# MARK: List Sessions

def list_sessions(args):
    """List all saved sessions, marking the currently active one with '*'."""
    try:
        all_creds = load_credentials()
    except json.JSONDecodeError:
        print(f"Error: credentials file is corrupted ({CREDENTIALS_FILE}).")
        return 1

    active = all_creds.get(ACTIVE_SESSION_KEY, "default")
    sessions = get_sessions(all_creds)

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


# MARK: Create Session

def create_session(args):
    """Login to CBRAIN and save credentials for the current session."""
    from cbrain_cli.cli_utils import all_credentials, api_token, cbrain_url, session_name

    if cbrain_url and api_token:
        print(f"Already logged in to session '{session_name}'. Use 'cbrain logout' to logout.")
        return 1

    server = getattr(args, "server", None) or input(
        "Enter CBRAIN server base URL [default: localhost:3000]: "
    ).strip() or DEFAULT_BASE_URL

    username = getattr(args, "username", None) or input("Enter CBRAIN username: ").strip()
    if not username:
        print("Username is required")
        return 1

    password = getattr(args, "password", None) or getpass.getpass("Enter CBRAIN password: ")
    if not password:
        print("Password is required")
        return 1

    encoded = urllib.parse.urlencode({"login": username, "password": password}).encode()
    request = urllib.request.Request(
        f"{server}/session", data=encoded, headers=DEFAULT_HEADERS, method="POST"
    )

    with urllib.request.urlopen(request) as resp:
        data = json.loads(resp.read())
        token = data.get("cbrain_api_token")
        if not token:
            print("Login failed: No API token received")
            return 1

        all_credentials[session_name] = {
            "cbrain_url": server,
            "api_token": token,
            "user_id": data.get("user_id"),
            "username": username,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        save_credentials(all_credentials)

    print(f"Connection successful. Token saved in {CREDENTIALS_FILE} for session '{session_name}'.")
    return 0


# MARK: Logout

def logout_session(args):
    """
    Logout from CBRAIN.

    Without ``--session``: logout all active sessions.
    With ``--session <name>``: logout only that session.
    """
    from cbrain_cli.cli_utils import session_name, session_specified

    # Load a fresh, unstripped copy from disk so _active_session is preserved.
    all_creds = load_credentials()
    sessions = get_sessions(all_creds)

    sessions_to_logout = list(sessions) if not session_specified else [session_name]

    if not sessions_to_logout:
        print("No active sessions to logout.")
        return 0

    for s_name in sessions_to_logout:
        creds = sessions.get(s_name, {})
        s_url, s_token = creds.get("cbrain_url"), creds.get("api_token")

        if not s_url or not s_token:
            if s_name in sessions:
                print(f"Invalid credentials for session '{s_name}'. Removing local session.")
                all_creds.pop(s_name, None)
            elif session_specified:
                print(f"Not logged in to session '{s_name}'.")
            elif len(sessions_to_logout) == 1:
                print("Not logged in. Use 'cbrain login' to login first.")
            continue

        # Use the stored username for the logout message (no extra network call needed).
        display_name = creds.get("username", s_name)

        try:
            req = urllib.request.Request(
                f"{s_url}/session", headers=auth_headers(s_token), method="DELETE"
            )
            with urllib.request.urlopen(req) as resp:
                if resp.status == 200:
                    print(f"Successfully logged out from CBRAIN server as {display_name}.")
                else:
                    print(f"Logout failed for session '{s_name}'.")
        except urllib.error.HTTPError as e:
            print(
                f"Session '{s_name}' already expired on server."
                if e.code == 401
                else f"Logout request failed for '{s_name}': HTTP {e.code}"
            )
        except urllib.error.URLError as e:
            print(f"Network error during logout for '{s_name}': {e}")

        all_creds.pop(s_name, None)
        print(f"Local session '{s_name}' removed from {CREDENTIALS_FILE}.")

    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(all_creds, f, indent=2)
    return 0

