import json
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url
from cbrain_cli.config import auth_headers


def show_tool(args):
    """
    Show tool details or list all tools.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including the tool argument with tool_id if specified
    """

    # Get the tool ID from the -id argument if provided.
    tool_id = getattr(args, "id", None)

    # Always use the tools endpoint (no individual tool endpoint available).
    tools_endpoint = f"{cbrain_url}/tools"

    headers = auth_headers(api_token)

    # Create the request.
    request = urllib.request.Request(
        tools_endpoint, data=None, headers=headers, method="GET"
    )

    # Make the request.
    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        tools_data = json.loads(data)

    if tool_id:
        # Filter and show details for a specific tool.
        if isinstance(tools_data, list):
            tool = None
            for t in tools_data:
                if t.get("id") == tool_id:
                    tool = t
                    break

            if tool:
                print(
                    f"id: {tool.get('id', 'N/A')}\n"
                    f"name: {tool.get('name', 'N/A')}\n"
                    f"user_id: {tool.get('user_id', 'N/A')}\n"
                    f"group_id: {tool.get('group_id', 'N/A')}\n"
                    f"category: {tool.get('category', 'N/A')}\n"
                    f"description: {tool.get('description', 'N/A')}\n"
                    f"url: {tool.get('url', 'N/A')}\n"
                )
            else:
                print(f"Error: Tool with ID {tool_id} not found")
                return 1
        else:
            print("Error: Unexpected response format from server")
            return 1
    else:
        # List all tools.
        if isinstance(tools_data, list):
            print(f"Found {len(tools_data)} tools:")
            print(f"{'ID':<5} {'Name':<20} {'Category':<20} {'Description':<30}")
            print("-" * 80)
            for tool in tools_data:
                tool_id = str(tool.get("id", "N/A"))
                name = tool.get("name", "N/A")[:19]
                category = tool.get("category", "N/A")[:19]
                description = tool.get("description", "N/A")[:29]
                print(f"{tool_id:<5} {name:<20} {category:<20} {description:<30}")
        else:
            print("No tools found or unexpected response format.")

    return 0
