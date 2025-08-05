import json
import urllib.parse
import urllib.request

from cbrain_cli.cli_utils import api_token, cbrain_url 
from cbrain_cli.config import auth_headers


def list_tool_configs(args):
    """
    Lists all tool configurations available in the system.

    Sends a GET request to the tool configurations endpoint to retrieve 
    a list of all tool configurations. The response is then parsed and returned as a JSON object.

    Returns
    -------
    list
        A list of tool configurations, each represented as a dictionary containing configuration details.
    """ 
    tool_configs_endpoint = f"{cbrain_url}/tool_configs"
    headers = auth_headers(api_token)

    request = urllib.request.Request(
        tool_configs_endpoint, data=None, headers=headers, method="GET"
    )

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        response_data = json.loads(data)
        return response_data


def show_tool_config(args):
    """
    Retrieves detailed information about a specific tool configuration.

    Detailed information about a specific tool configuration. 

    Returns
    -------
    dict
        A dictionary containing the detailed information for the specified tool configuration.
    """
    show_tool_config_endpoint = f"{cbrain_url}/tool_configs/{args.id}"
    headers = auth_headers(api_token)

    request = urllib.request.Request(
        show_tool_config_endpoint, data=None, headers=headers, method="GET"
    )

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        response_data = json.loads(data)
        return response_data
    
def tool_config_boutiques_descriptor(args):
    """
    Retrieves the Boutiques descriptor for a specific tool configuration.

    Sends a GET request to the tool configuration Boutiques descriptor endpoint 
    to retrieve the descriptor for a specific tool configuration. 
    The response is then parsed and returned as a JSON object.

    Returns
    -------
    dict
        A dictionary containing the Boutiques descriptor for the specified tool configuration.
    """
    tool_config_boutiques_descriptor_endpoint = f"{cbrain_url}/tool_configs/{args.id}/boutiques_descriptor"
    headers = auth_headers(api_token)

    request = urllib.request.Request(
        tool_config_boutiques_descriptor_endpoint, data=None, headers=headers, method="GET"
    )

    with urllib.request.urlopen(request) as response:
        data = response.read().decode("utf-8")
        response_data = json.loads(data)
        return response_data    

