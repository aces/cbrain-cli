import configparser
import functools
import importlib.metadata
import json
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from cbrain_cli import config as cbrain_config
from cbrain_cli.config import DEFAULT_HEADERS, DEFAULT_TIMEOUT, auth_headers

_debug = False


def set_debug(flag: bool) -> None:
    """Enable or disable debug output."""
    global _debug
    _debug = bool(flag)


def debug_log(message: str) -> None:
    """Print a debug line to stderr when debug mode is active."""
    if _debug:
        print(f"[DEBUG] {message}", file=sys.stderr)


class CbrainClient:
    """
    Holds auth state and issues JSON requests against a CBRAIN server.
    """

    def __init__(self, base_url, token=None, user_id=None, timeout=None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.user_id = user_id
        self.timeout = timeout if timeout is not None else DEFAULT_TIMEOUT

    @classmethod
    def from_credentials(cls, timeout=None):
        """
        Build a client from the saved credentials file.
        """
        creds = cbrain_config.load_credentials() or {}
        return cls(
            creds.get("cbrain_url", ""),
            creds.get("api_token", ""),
            creds.get("user_id"),
            timeout,
        )

    def _request(self, method, path, *, headers=None, body=None, params=None):
        """
        Issue an HTTP request and return (raw_bytes, status).
        """
        target = path if path.startswith(("http://", "https://")) else f"{self.base_url}{path}"
        if params:
            target = f"{target}?{urllib.parse.urlencode(params)}"
        hdrs = headers or auth_headers(self.token)
        # strip host from full URL for debug display; preserve all query params
        parsed = urllib.parse.urlsplit(target)
        display_path = parsed.path
        if display_path.startswith(self.base_url):
            display_path = display_path[len(self.base_url) :]
        query = urllib.parse.urlencode(params) if params else parsed.query
        if query:
            display_path = f"{display_path}?{query}"
        debug_log(f"{method} {display_path}")
        req = urllib.request.Request(target, data=body, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                status = r.status
                debug_log(f"→ HTTP {status}")
                return r.read(), status
        except urllib.error.HTTPError as e:
            debug_log(f"→ HTTP {e.code} ({e.reason})")
            raise CliApiError(e.reason or f"HTTP {e.code}", status=e.code) from e

    def get(self, path, params=None):
        """
        Authenticated GET; returns parsed JSON.
        """
        raw, _ = self._request("GET", path, params=params)
        return json.loads(raw.decode())

    def send(self, method, path, payload=None):
        """
        Authenticated POST/PUT/DELETE with optional JSON body; returns (parsed, status).
        """
        hdrs = auth_headers(self.token)
        body = None
        if payload is not None:
            hdrs["Content-Type"] = "application/json"
            body = json.dumps(payload).encode()
        raw, status = self._request(method, path, headers=hdrs, body=body)
        decoded = raw.decode()
        return (json.loads(decoded) if decoded.strip() else {}), status

    def post_form(self, path, form_data, headers=None):
        """
        POST form-urlencoded data (unauthenticated); returns parsed JSON.
        """
        hdrs = headers or DEFAULT_HEADERS
        body = urllib.parse.urlencode(form_data).encode()
        raw, _ = self._request("POST", path, headers=hdrs, body=body)
        return json.loads(raw.decode())

    def post_multipart(self, path, body, content_type):
        """
        Authenticated multipart POST; returns (parsed JSON, status).
        """
        hdrs = auth_headers(self.token)
        hdrs["Content-Type"] = content_type
        hdrs["Content-Length"] = str(len(body))
        raw, status = self._request("POST", path, headers=hdrs, body=body)
        return json.loads(raw.decode()), status


PAGINATABLE_ACTIONS = {
    ("file", "list"),
    ("data-provider", "list"),
    ("tool", "list"),
    ("tool-config", "list"),
    ("tag", "list"),
    ("task", "list"),
}


class CliValidationError(Exception):
    """Raised when command arguments fail client-side validation.

    Parameters
    ----------
    message : str
        Human-readable error description.
    field : str, optional
        The CLI flag or argument name that caused the error (e.g. ``--per-page``).
    """

    def __init__(self, message, field=None):
        super().__init__(message)
        self.field = field

    def __str__(self):
        message = self.args[0] if self.args else ""
        if self.field:
            return f"{message} ({self.field})"
        return message


class CliApiError(Exception):
    """
    Raised when the API returns an expected error response.
    """

    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


class CliResponseError(Exception):
    """
    Raised when the API response is malformed or unexpected.
    """

    pass


def is_authenticated():
    """
    Check if the user is authenticated.
    """
    client = CbrainClient.from_credentials()
    if not client.token or not client.base_url or not client.user_id:
        print("Not logged in. Use 'cbrain login' to login first.")
        return False
    return True


def get_status_code_description(status_code):
    """
    Get a user-friendly description for HTTP status codes.

    Parameters
    ----------
    status_code : int
        HTTP status code

    Returns
    -------
    str
        Description of the status code category
    """
    if 400 <= status_code < 500:
        if status_code == 401:
            return "Authentication error (401)"
        elif status_code == 403:
            return "Access forbidden (403)"
        elif status_code == 404:
            return "Resource not found (404)"
        elif status_code == 422:
            return "Validation error (422)"
        else:
            return f"Client error ({status_code})"
    elif 500 <= status_code < 600:
        return f"Server error ({status_code})"
    else:
        return f"HTTP error ({status_code})"


def handle_connection_error(error):
    """
    Handle connection errors with informative messages including server URL.

    Parameters
    ----------
    error : Exception
        The connection error that occurred

    Returns
    -------
    None
        Prints appropriate error messages
    """
    if isinstance(error, urllib.error.HTTPError):
        status_description = get_status_code_description(error.code)

        if error.code == 401:
            print(f"{status_description}: {error.reason}")
            print("Error: Session expired or invalid. Run 'cbrain logout' then 'cbrain login'.")
        elif error.code in (400, 404, 422, 500):
            # Try to extract specific error message from response
            try:
                # Check if the error response has already been read
                if hasattr(error, "read"):
                    error_response = error.read().decode("utf-8")
                elif hasattr(error, "response") and hasattr(error.response, "read"):
                    error_response = error.response.read().decode("utf-8")
                else:
                    error_response = ""

                # Try to parse as JSON first (for 422 validation errors)
                try:
                    error_data = json.loads(error_response)
                    if isinstance(error_data, dict):
                        # Look for common error message fields
                        error_msg = str(
                            error_data.get("message")
                            or error_data.get("error")
                            or error_data.get("notice")
                            or error_data
                        )
                        # Check if this looks like a password change redirect
                        if "change_password" in error_msg:
                            print(
                                f"{status_description}: Account requires "
                                "a password change. "
                                "Please log into the web portal."
                            )
                            return
                        print(f"{status_description}: {error_msg}")
                        return
                except json.JSONDecodeError:
                    # Not JSON, try HTML parsing
                    pass

                # Extract header h1 and h2 content from HTML
                header_pattern = r"<header>\s*<h1>(.*?)</h1>\s*</header>"
                header_match = re.search(header_pattern, error_response, re.DOTALL)
                h2_match = re.search(r"<h2>(.*?)</h2>", error_response)

                error_parts = []

                if header_match:
                    header_text = header_match.group(1).strip()
                    # Decode HTML entities
                    header_text = header_text.replace("&#39;", "'").replace("&quot;", '"')
                    error_parts.append(header_text)

                if h2_match:
                    h2_text = h2_match.group(1).strip()
                    # Decode HTML entities
                    h2_text = h2_text.replace("&#39;", "'").replace("&quot;", '"')
                    # Remove SQL WHERE clause details
                    h2_text = re.sub(r"\s*\[WHERE.*?\]", "", h2_text)
                    error_parts.append(h2_text)

                if error_parts:
                    print(f"{status_description}: " + " - ".join(error_parts))
                else:
                    print(f"{status_description}: {error.reason}")
            except Exception:
                print(f"{status_description}: {error.reason}")
        else:
            print(f"{status_description}: {error.reason}")
    elif isinstance(error, urllib.error.URLError):
        if isinstance(error.reason, socket.timeout):
            print(
                f"Error: Request timed out after {DEFAULT_TIMEOUT}s. "
                "Check your connection or set CBRAIN_TIMEOUT env var."
            )
        elif "Connection refused" in str(error):
            print(
                "Error: Cannot connect to CBRAIN server at "
                f"{CbrainClient.from_credentials().base_url}"
            )
            print("Please check if the CBRAIN server is running and accessible.")
        else:
            print(f"Connection failed: {error.reason}")
    else:
        print(f"Connection error: {str(error)}")


def handle_errors(func):
    """
    Decorator to handle common errors for all CLI commands.

    Returns
    -------
    None
        A command is run via inputs from the user.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except json.JSONDecodeError:
            print("Failed: Invalid response from server")
            return 1
        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return 1
        except (CliValidationError, CliResponseError) as e:
            print(f"Error: {e}")
            return 1
        except CliApiError as e:
            if isinstance(e.__cause__, urllib.error.HTTPError):
                handle_connection_error(e.__cause__)
            else:
                print(f"Error: {e}")
            return 1
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            handle_connection_error(e)
            return 1
        except socket.timeout as e:
            handle_connection_error(urllib.error.URLError(e))
            return 1
        except Exception as e:
            print(f"Operation failed: {e}")
            return 1

    return wrapper


def version_info(args):
    """
    Display the CLI version information.

    Prefer installed package metadata; fall back to setup.cfg when running
    from a source tree without install.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    try:
        cbrain_cli_version = importlib.metadata.version("cbrain-cli")
    except importlib.metadata.PackageNotFoundError:
        cfg = configparser.ConfigParser()
        cfg.read(Path(__file__).resolve().parents[1] / "setup.cfg")
        cbrain_cli_version = cfg["metadata"]["version"]

    if output_json(args, {"version": cbrain_cli_version}):
        return 0
    print(f"cbrain cli client version {cbrain_cli_version}")
    return 0


def output_json(args, data):
    """
    Print data as JSON or JSONL if requested. Returns True if output was handled.
    """
    if getattr(args, "json", False):
        json_printer(data)
        return True
    if getattr(args, "jsonl", False):
        jsonl_printer(data)
        return True
    return False


def confirm_destructive(args, prompt):
    """
    Gate destructive actions: ``--yes`` skips, TTY asks, otherwise refuse.

    Returns
    -------
    bool
        True to proceed, False if the user declined an interactive prompt.
    """
    if getattr(args, "yes", False):
        return True
    # JSON/JSONL must not mix with a prompt; pipes/EOF also never auto-confirm.
    if getattr(args, "json", False) or getattr(args, "jsonl", False) or not sys.stdin.isatty():
        raise CliValidationError(
            "Refusing destructive action without confirmation; pass --yes",
            field="--yes",
        )
    try:
        answer = input(f"{prompt} [y/N]: ").strip().lower()
    except EOFError:
        print("Aborted.")
        return False
    if answer in ("y", "yes"):
        return True
    print("Aborted.")
    return False


def display_key_value_table(pairs):
    """
    Print a (key-value) two-column Field/Value table from a list of (field, value) tuples.
    """
    rows = [{"field": k, "value": v} for k, v in pairs]
    dynamic_table_print(rows, ["field", "value"], ["Field", "Value"])


def json_printer(data):
    """
    Print data in JSON format.
    """
    print(json.dumps(data, indent=2))


def jsonl_printer(data):
    """
    Print data in JSONL format.
    Each object is printed as a single line of JSON with no indentation.
    For lists, each object is separated by newlines with no commas or enclosing brackets.
    """
    if isinstance(data, list):
        for item in data:
            print(json.dumps(item, separators=(",", ":")))
    else:
        print(json.dumps(data, separators=(",", ":")))


def pagination(args, query_params):
    """
    Validate the per_page parameter.
    """
    per_page = getattr(args, "per_page", 25)
    if per_page < 5 or per_page > 1000:
        raise CliValidationError("per-page must be between 5 and 1000", field="--per-page")

    page = getattr(args, "page", 1)
    if page < 1:
        raise CliValidationError("page must be 1 or greater", field="--page")

    query_params["page"] = str(page)
    query_params["per_page"] = str(per_page)

    return query_params


def dynamic_table_print(
    data,
    columns,
    headers=None,
    wrap_columns=None,
    max_total_width=None,
    max_column_widths=None,
    indent_wrapped=True,
    max_row_lines=None,
    preserve_blank_lines=False,
):
    """
    Print data in a dynamically-sized table format with proper column alignment.

    Parameters
    ----------
    data : list of dict
        List of dictionaries containing the data to display
    columns : list of str
        List of column keys to extract from each data dictionary
    headers : list of str, optional
        List of header names. If None, uses the column keys as headers

    Returns
    -------
    None
        Prints the formatted table to stdout

    Examples
    --------
    >>> data = [
    ...     {"id": 1234567, "type": "ReconAllCrossSectionalOutput", "name": "file1.txt"},
    ...     {"id": 5, "type": "SingleFile", "name": "demo.txt"}
    ... ]
    >>> dynamic_table_print(data, ["id", "type", "name"], ["ID", "Type", "File Name"])
    """
    if not data:
        print("No data found.")
        return

    # Lazy imports to avoid adding global deps when not needed
    import shutil
    import textwrap

    # Use column keys as headers if none provided
    if headers is None:
        headers = columns

    if len(headers) != len(columns):
        raise ValueError("Number of headers must match number of columns")

    wrap_columns = set(wrap_columns or [])
    max_column_widths = max_column_widths or {}

    # Determine target total width (terminal width by default)
    if max_total_width is None:
        try:
            max_total_width = shutil.get_terminal_size(fallback=(120, 24)).columns
        except Exception:
            max_total_width = 120

    # Compute base widths for non-wrapped columns; headers included
    base_widths = []
    for column, header in zip(columns, headers):
        max_data_width = max(len(str(item.get(column, ""))) for item in data)
        width = max(max_data_width, len(str(header)))
        # Apply per-column maximums if provided
        if column in max_column_widths:
            width = min(width, int(max_column_widths[column]))
        base_widths.append(width)

    # If wrapping is requested, allocate space to wrapped columns within terminal width
    spaces_between = max(len(columns) - 1, 0)  # single space between columns
    non_wrapped_indices = [i for i, c in enumerate(columns) if c not in wrap_columns]
    wrapped_indices = [i for i, c in enumerate(columns) if c in wrap_columns]

    column_widths = list(base_widths)

    if wrapped_indices:
        non_wrapped_total = sum(base_widths[i] for i in non_wrapped_indices)
        available_for_wrapped = max_total_width - non_wrapped_total - spaces_between
        # Distribute available width across wrapped columns (usually one).
        num_wrapped = max(len(wrapped_indices), 1)
        per_wrapped = max(1, available_for_wrapped // num_wrapped)
        for idx in wrapped_indices:
            header_len = len(str(headers[idx]))
            # Try to stay within terminal width budget; if header is larger we accept overflow.
            column_widths[idx] = max(per_wrapped, header_len)

    # Print header and matching separator
    header_parts = []
    separator_parts = []
    for header, width in zip(headers, column_widths):
        header_parts.append(f"{str(header):<{width}}")
        separator_parts.append("-" * width)

    print(" ".join(header_parts))
    print(" ".join(separator_parts))

    # Print each row with wrapping where requested.
    for item in data:
        wrapped_cells = []
        max_lines = 1
        for col, width in zip(columns, column_widths):
            raw_value = str(item.get(col, ""))
            if col in wrap_columns and width > 0:
                # Preserve explicit newlines by wrapping each paragraph separately.
                paragraphs = str(raw_value).splitlines() or [""]
                lines: list[str] = []
                for para in paragraphs:
                    if para == "":
                        if preserve_blank_lines:
                            lines.append("")
                        continue
                    lines.extend(
                        textwrap.wrap(
                            para,
                            width=width,
                            replace_whitespace=False,
                            drop_whitespace=False,
                            break_long_words=True,
                            break_on_hyphens=True,
                        )
                    )
                wrapped = lines if lines else [""]
            else:
                wrapped = [raw_value]
            wrapped_cells.append(wrapped)
            if len(wrapped) > max_lines:
                max_lines = len(wrapped)

        # Determine how many lines we will display for this row.
        visible_lines = max_lines if max_row_lines is None else min(max_lines, int(max_row_lines))

        # Emit lines for the tallest wrapped cell (capped by visible_lines).
        for line_idx in range(visible_lines):
            row_parts = []
            for (col, width), cell_lines in zip(zip(columns, column_widths), wrapped_cells):
                text = cell_lines[line_idx] if line_idx < len(cell_lines) else ""
                truncated_here = False

                # Indent continuation lines for wrapped columns.
                if line_idx > 0 and indent_wrapped and col in wrap_columns:
                    indent = "  " if width > 2 else ""
                    text = indent + text

                # If this is the last visible line and there are more lines, append ellipsis
                if (
                    col in wrap_columns
                    and line_idx == visible_lines - 1
                    and len(cell_lines) > visible_lines
                ):
                    truncated_here = True

                # Ensure we do not overflow column width; append ellipsis if truncated.
                if len(text) > width:
                    # Hard truncate to width
                    text = text[:width]
                    truncated_here = True

                if truncated_here and width >= 1:
                    # Add an ellipsis within the width, prefer '...' but scale down if tight.
                    ellipsis = "..." if width >= 3 else "." * width
                    # Reserve space for ellipsis when possible.
                    if width >= 3:
                        text = text[: max(0, width - len(ellipsis))] + ellipsis
                    else:
                        text = ellipsis

                row_parts.append(f"{text:<{width}}")
            print(" ".join(row_parts).rstrip())
