from cbrain_cli.cli_utils import (
    CliApiError,
    CliValidationError,
    api_get,
    api_token,
    cbrain_url,
    pagination,
)


def list_tools(args):
    """
    Get paginated list of tools from CBRAIN.
    """
    params = pagination(args, {})
    return api_get(f"{cbrain_url}/tools", api_token, params)


def show_tool(args):
    """
    Get detailed information about a specific tool from CBRAIN.

    Searches paginated ``GET /tools`` results because ``GET /tools/{id}``
    returns 204 No Content on this API.
    """
    tool_id = getattr(args, "id", None)
    if not tool_id:
        raise CliValidationError("Tool ID is required", field="id")

    per_page = 20
    page = 1
    while True:
        tools_page = api_get(
            f"{cbrain_url}/tools",
            api_token,
            {"page": str(page), "per_page": str(per_page)},
        )
        if not tools_page:
            break
        for tool in tools_page:
            if tool.get("id") == tool_id:
                return tool
        if len(tools_page) < per_page:
            break
        page += 1

    raise CliApiError(f"Tool with ID {tool_id} not found")
