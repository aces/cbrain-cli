import datetime
import functools
import json
import urllib.error
# import importlib.metadata

from cbrain_cli.config import CREDENTIALS_FILE

try:
    # MARK: Credentials.
    with open(CREDENTIALS_FILE, "r") as f:
        credentials = json.load(f)

    # Get credentials.
    cbrain_url = credentials.get("cbrain_url")
    api_token = credentials.get("api_token")
    user_id = credentials.get("user_id")
    cbrain_timestamp = credentials.get("timestamp")
except FileNotFoundError:
    cbrain_url = None
    api_token = None
    user_id = None
    cbrain_timestamp = None


def is_authenticated():
    """
    Check if the user is authenticated.
    """

    if cbrain_timestamp:
        timestamp_obj = datetime.datetime.fromisoformat(cbrain_timestamp)
        if datetime.datetime.now() - timestamp_obj > datetime.timedelta(days=1):
            print("Session expired. Please log in again using 'cbrain login'.")
            CREDENTIALS_FILE.unlink()
            return False
    # Check if user is logged in.
    if not api_token or not cbrain_url or not user_id:
        print("Not logged in. Use 'cbrain login' to login first.")
        return False
    return True


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
    if isinstance(error, urllib.error.URLError):
        if "Connection refused" in str(error):
            print(f"Error: Cannot connect to CBRAIN server at {cbrain_url}")
            print("Please check if the CBRAIN server is running and accessible.")
        else:
            print(f"Connection failed: {error.reason}")
    elif isinstance(error, urllib.error.HTTPError):
        print(f"Request failed: HTTP {error.code} - {error.reason}")
        if error.code == 401:
            print("Invalid username or password")
        elif error.code == 404:
            print("Resource not found")
        elif error.code == 500:
            print("Internal server error")
    else:
        print(f"Connection error: {str(error)}")


def handle_errors(func):
    """
    Decorator to handle common errors for all CLI commands.

    Returns
    -------
    None
        A command is ran via inputs from the user.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except urllib.error.HTTPError as e:
            handle_connection_error(e)
            return 1
        except urllib.error.URLError as e:
            handle_connection_error(e)
            return 1
        except json.JSONDecodeError:
            print("Failed: Invalid response from server")
            return 1
        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return 1
        except Exception as e:
            print(f"Operation failed: {str(e)}")
            return 1

    return wrapper

def version_info(args):
    """
    Display the CLI version information.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    print("cbrain cli client version 1.0")
    # try:
    #     cbrain_cli_version = importlib.metadata.version('cbrain-cli') 
    #     print(f"cbrain cli client version {cbrain_cli_version}")
    #     return 0
    # except importlib.metadata.PackageNotFoundError:
    #     print("Warning: Could not determine version. Package may not be installed properly.")
    #     return 1

def json_printer(data):
    """
    Print data in JSON format.
    """
    print(json.dumps(data, indent=2))
    return 0

def jsonl_printer(data):
    """
    Print data in JSONL format.
    Each object is printed as a single line of JSON with no indentation.
    For lists, each object is separated by newlines with no commas or enclosing brackets.
    """
    if isinstance(data, list):
        for item in data:
            print(json.dumps(item, separators=(',', ':')))
    else:
        print(json.dumps(data, separators=(',', ':')))
    return 0

def pagination(args,query_params):
    """
    Validate the per_page parameter.
    """
    per_page = getattr(args, "per_page", 25)
    if per_page < 5 or per_page > 1000:
        print("Error: per-page must be between 5 and 1000")
        return None
    
    page = getattr(args, "page", 1)
    if page < 1:
        print("Error: page must be 1 or greater")
        return None
        
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
                    lines.extend(textwrap.wrap(
                        para,
                        width=width,
                        replace_whitespace=False,
                        drop_whitespace=False,
                        break_long_words=True,
                        break_on_hyphens=True,
                    ))
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
                if col in wrap_columns and line_idx == visible_lines - 1 and len(cell_lines) > visible_lines:
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