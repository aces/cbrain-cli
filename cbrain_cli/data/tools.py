from cbrain_cli.cli_utils import (
    CliApiError,
    CliResponseError,
    CliValidationError,
    api_get,
    api_token,
    cbrain_url,
    pagination,
)


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
    # Get the tool ID from the id argument if provided.
    tool_id = getattr(args, "id", None)
    if tool_id is None and getattr(args, "action", None) == "show":
        raise CliValidationError("Tool ID is required", field="id")
    params = pagination(args, {})
    tools_data = api_get(f"{cbrain_url}/tools", api_token, params)

    if not isinstance(tools_data, list):
        raise CliResponseError("Unexpected response format from server")

    if tool_id:
        # Filter for a specific tool
        tool = next((t for t in tools_data if t.get("id") == tool_id), None)
        if not tool:
            raise CliApiError(f"Tool with ID {tool_id} not found")
        return tool

    return tools_data
