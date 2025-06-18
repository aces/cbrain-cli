import json
import urllib.request
 
from cbrain_cli.config import auth_headers, CREDENTIALS_FILE
from cbrain_cli.cli_utils import cbrain_url, api_token, user_id

headers = auth_headers(api_token)

def user_details(user_id):
    """
    Get user name from user ID.
    """
    # Get user details.
    user_endpoint = f"{cbrain_url}/users/{user_id}"
    
    user_request = urllib.request.Request(
        user_endpoint,
        headers=headers,
        method='GET'
    )
    
    try:
        with urllib.request.urlopen(user_request) as response:
            user_data = json.loads(response.read().decode('utf-8'))
            return user_data 
        
    except Exception as e:
        print(f"Error getting user details: {e}")
        return 1

 # MARK: Whoami
def whoami_user(args):
    """
    Display current user information by getting user details from server.
    Returns
    -------
    None
        Prints current user information.
    """
    version = getattr(args, 'version', False)
    user_data = user_details(user_id)

    # Check if logged in.
    if not CREDENTIALS_FILE.exists():
        print("Not logged in. Please login with 'cbrain login'.")
        return 
    
 
    if not cbrain_url or not api_token or not user_id:
        print("Invalid credentials file. Please login again.")
        return 
    
    if version:    
        # Show masked token.
        masked_token = api_token[:2] + '*' * (len(api_token) - 4) + api_token[-2:] if len(api_token) > 4 else '****'
    
        print(f"DEBUG: Found credentials {CREDENTIALS_FILE}")
        print(f"DEBUG: User in credentials: {user_data['login']} on server {cbrain_url}")
        print(f"DEBUG: Token found: {masked_token}")
        print("DEBUG: Verifying token...")
        print("DEBUG: GET /session")
        
        # Verify token by making a session request.
        session_endpoint = f"{cbrain_url}/session"
        
        session_request = urllib.request.Request(
            session_endpoint,
            headers=headers,
            method='GET'
        )
        
        try:
            with urllib.request.urlopen(session_request) as response:
                session_data = json.loads(response.read().decode('utf-8'))
            
                print(f"DEBUG: Got JSON reply {json.dumps(session_data)}")
                
                # Verify local credentials match server response.
                remote_user_id = session_data.get('user_id')
                remote_token = session_data.get('cbrain_api_token')
                
                if str(remote_user_id) != str(user_id):
                    print(f"WARNING: User ID mismatch - Local: {user_id}, Remote: {remote_user_id}")
                
                if remote_token != api_token:
                    print("WARNING: Token mismatch - tokens don't match")
                
                print(f"DEBUG: GET /users/{remote_user_id}")
                print(f"DEBUG: Got JSON reply {json.dumps(user_details(remote_user_id))}")
                    
        except Exception as e:
            print(f"Error verifying session: {e}")
            return 1
    
    print(f"Current user: {user_data['login']} ({user_data['full_name']}) on server {cbrain_url}")  
