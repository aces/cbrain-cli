import json
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url, pagination
from cbrain_cli.config import auth_headers


def list_tools(args):
    """
    Get tool details or list of all tools.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the tool argument with tool_id if specified

    Returns
    -------
    dict or list or None
        - dict: when tool_id is provided and found
        - list: when no tool_id is provided
        - None: when error occurs or tool not found
    """
    # Get the tool ID from the -id argument if provided.
    tool_id = getattr(args, "id", None)
    query_params = {}
    query_params = pagination(args,query_params)

    tools_endpoint = f"{cbrain_url}/tools"
    query_string = urllib.parse.urlencode(query_params)
    tools_endpoint = f"{tools_endpoint}?{query_string}"
    headers = auth_headers(api_token)

    request = urllib.request.Request(
        tools_endpoint, data=None, headers=headers, method="GET"
    )

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        tools_data = json.loads(data)

    if not isinstance(tools_data, list):
        print("Error: Unexpected response format from server")
        return None

    if tool_id:
        # Filter for a specific tool
        tool = next((t for t in tools_data if t.get("id") == tool_id), None)
        if not tool:
            print(f"Error: Tool with ID {tool_id} not found")
            return None
        return tool
    else:
        # Return all tools
        return tools_data
