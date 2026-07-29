from cbrain_cli.cli_utils import (
    CbrainClient,
    CliValidationError,
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
    return CbrainClient.from_credentials().get("/tool_configs", params=params)


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
    return CbrainClient.from_credentials().get(f"/tool_configs/{config_id}")


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
    return CbrainClient.from_credentials().get(f"/tool_configs/{config_id}/boutiques_descriptor")
