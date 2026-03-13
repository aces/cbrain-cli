"""
CBRAIN CLI Configuration
"""

from pathlib import Path

# Default settings.
DEFAULT_BASE_URL = "http://localhost:3000"

# Session file configuration.
SESSION_FILE_DIR = Path.home() / ".config" / "cbrain-cli"
SESSION_FILE_NAME = "credentials.json"
SESSION_FILE_DIR.mkdir(parents=True, exist_ok=True)
CREDENTIALS_FILE = SESSION_FILE_DIR / SESSION_FILE_NAME

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
