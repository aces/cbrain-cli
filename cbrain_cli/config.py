"""
CBRAIN CLI Configuration
"""

import json
import os
from pathlib import Path

# Default settings.
DEFAULT_BASE_URL = "http://localhost:3000"

# Session file configuration.
SESSION_FILE_DIR = Path.home() / ".config" / "cbrain"
SESSION_FILE_NAME = "credentials.json"
CREDENTIALS_FILE = SESSION_FILE_DIR / SESSION_FILE_NAME
DEFAULT_CREDENTIALS_MODE = 0o600

# HTTP request timeout in seconds; override with CBRAIN_TIMEOUT env var.
try:
    DEFAULT_TIMEOUT = max(1, int(os.environ.get("CBRAIN_TIMEOUT", "30")))
except ValueError:
    DEFAULT_TIMEOUT = 30

# Key used inside credentials.json to track the currently active session.
# Prefixed with "_" so it is clearly not a session name.
ACTIVE_SESSION_KEY = "_active_session"

# HTTP headers.
DEFAULT_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
}


def auth_headers(api_token):
    """
    Generate authorization headers with API token.

    Parameters
    ----------
    api_token : str
        The API token for authorization

    Returns
    -------
    dict
        Headers dictionary with authorization
    """
    return {"Accept": "application/json", "Authorization": f"Bearer {api_token}"}


def load_credentials():
    """
    Load credentials from the session file.
    """
    try:
        with open(CREDENTIALS_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def is_flat_credentials(data):
    """True when file is single-session (api_token at top level), not named map."""
    if not isinstance(data, dict) or not data:
        return False
    if "api_token" in data or "cbrain_url" in data:
        return not any(
            k != ACTIVE_SESSION_KEY
            and isinstance(v, dict)
            and ("api_token" in v or "cbrain_url" in v)
            for k, v in data.items()
        )
    return False


def get_named_sessions(data):
    """Return {name: creds} for flat or multi-session files."""
    if not data:
        return {}
    if is_flat_credentials(data):
        return {"default": {k: v for k, v in data.items() if k != ACTIVE_SESSION_KEY}}
    return {k: v for k, v in data.items() if k != ACTIVE_SESSION_KEY and isinstance(v, dict)}


def _cli_session_override():
    """Return --session name from argv when present."""
    from cbrain_cli.cli_utils import session_name, session_specified

    return session_name if session_specified else None


def cli_session_not_found():
    """Return session name when --session was given but is not saved locally."""
    from cbrain_cli.cli_utils import session_name, session_specified

    if not session_specified:
        return None
    if session_name in get_named_sessions(load_credentials() or {}):
        return None
    return session_name


def resolve_session_credentials(data, session_name=None):
    """Pick active session dict from flat or multi-session credentials file."""
    if not data:
        return {}
    if session_name is None:
        session_name = _cli_session_override()
    if is_flat_credentials(data):
        return {k: v for k, v in data.items() if k != ACTIVE_SESSION_KEY}
    name = session_name or data.get(ACTIVE_SESSION_KEY) or "default"
    entry = data.get(name)
    return dict(entry) if isinstance(entry, dict) else {}


def update_active_credentials(updates=None, remove_keys=None, session_name=None):
    """Patch fields on the active (or named) session; supports flat + nested files."""
    data = load_credentials()
    if data is None:
        return
    updates = updates or {}
    remove_keys = remove_keys or []
    if session_name is None:
        session_name = _cli_session_override()
    if is_flat_credentials(data):
        data.update(updates)
        for k in remove_keys:
            data.pop(k, None)
        save_credentials(data)
        return
    name = session_name or data.get(ACTIVE_SESSION_KEY) or "default"
    entry = dict(data.get(name) or {})
    entry.update(updates)
    for k in remove_keys:
        entry.pop(k, None)
    data[name] = entry
    save_credentials(data)


def save_credentials(credentials):
    """
    Save credentials to the session file.
    """
    CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)

    is_posix = os.name == "posix"

    if is_posix:
        # Preserve restrictive permissions when updating.
        if CREDENTIALS_FILE.exists():
            existing = CREDENTIALS_FILE.stat().st_mode & 0o777
            if existing & 0o077 == 0 and existing & 0o600 == 0o600:
                mode = existing
            else:
                mode = DEFAULT_CREDENTIALS_MODE
            if not os.access(CREDENTIALS_FILE, os.W_OK):
                os.chmod(CREDENTIALS_FILE, mode | 0o200)
            if mode != existing:
                os.chmod(CREDENTIALS_FILE, mode)
        else:
            mode = DEFAULT_CREDENTIALS_MODE

        # Create with user-private permissions where supported.
        fd = os.open(CREDENTIALS_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(credentials, f, indent=2)
        finally:
            try:
                os.chmod(CREDENTIALS_FILE, mode)
            except OSError:
                pass
    else:
        # Non-POSIX: skip permission handling.
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(credentials, f, indent=2)
