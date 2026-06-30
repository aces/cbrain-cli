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
