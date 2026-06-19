"""
CBRAIN CLI Configuration
"""

import json
from pathlib import Path

# Default settings.
DEFAULT_BASE_URL = "http://localhost:3000"

# Session file configuration.
SESSION_FILE_DIR = Path.home() / ".config" / "cbrain"
SESSION_FILE_NAME = "credentials.json"
CREDENTIALS_FILE = SESSION_FILE_DIR / SESSION_FILE_NAME

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
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f, indent=2)
