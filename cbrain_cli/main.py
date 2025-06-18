"""
Setup and commands for the CBRAIN CLI command line interface. 
"""

import argparse
import sys

from cbrain_cli.cli_utils import handle_errors 
from cbrain_cli.sessions import (
    create_session,
    logout_session
)
from cbrain_cli.version import whoami_user

def main():
    """
    The function that controls the CBRAIN CLI.

    Returns
    -------
    None
        A command is ran via inputs from the user.
    """
    parser = argparse.ArgumentParser(description='CBRAIN CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # MARK: Sessions
    # Create new session.
    login_parser = subparsers.add_parser('login', help='Login to CBRAIN')
    login_parser.set_defaults(func=handle_errors(create_session))

    # Logout session.
    logout_parser = subparsers.add_parser('logout', help='Logout from CBRAIN')
    logout_parser.set_defaults(func=handle_errors(logout_session))

    # Show current session.
    whoami_parser = subparsers.add_parser('whoami', help='Show current session')
    whoami_parser.add_argument('-v', '--version', action='store_true', help='Show version')
    whoami_parser.set_defaults(func=handle_errors(whoami_user))

    # MARK: Setup CLI
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 

    if args.command == 'login':
        return handle_errors(create_session)(args)
    elif args.command == 'logout':
        return handle_errors(logout_session)(args) 
    elif args.command == 'whoami':
        return handle_errors(whoami_user)(args)

    if hasattr(args, 'func'):
        return args.func(args)

if __name__ == '__main__':
    sys.exit(main()) 