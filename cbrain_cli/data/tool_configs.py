from cbrain_cli.cli_utils import (
    CliValidationError,
    api_get,
    api_token,
    cbrain_url,
    pagination,
)


def list_tool_configs(args):
    """
    Lists all tool configurations available in the system.

    Returns
    -------
    list
        A list of tool configurations, each represented as a dictionary containing
        configuration details.
    """
    params = pagination(args, {})
    return api_get(f"{cbrain_url}/tool_configs", api_token, params)


def show_tool_config(args):
    """
    Retrieves detailed information about a specific tool configuration.

    Returns
    -------
    dict
        A dictionary containing the detailed information for the specified tool configuration.
    """
    config_id = getattr(args, "id", None)
    if not config_id:
        raise CliValidationError("Tool configuration ID is required", field="id")
    return api_get(f"{cbrain_url}/tool_configs/{config_id}", api_token)


def tool_config_boutiques_descriptor(args):
    """
    Retrieves the Boutiques descriptor for a specific tool configuration.

    Returns
    -------
    dict
        A dictionary containing the Boutiques descriptor for the specified tool configuration.
    """
    config_id = getattr(args, "id", None)
    if not config_id:
        raise CliValidationError("Tool configuration ID is required", field="id")
    return api_get(
        f"{cbrain_url}/tool_configs/{config_id}/boutiques_descriptor", api_token
    )
