"""
Setup and commands for the CBRAIN CLI command line interface. 
"""

import argparse
import sys

from cbrain_cli.cli_utils import handle_errors, is_authenticated
from cbrain_cli.list import list_projects, list_files, list_data_providers
from cbrain_cli.files import show_file, upload_file
from cbrain_cli.tool import show_tool
from cbrain_cli.dataProviders import show_data_provider
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

    # List of user details.
    list_parser = subparsers.add_parser('list', help='List')
    list_parser.add_argument('-j', '--json', action='store_true', help='Output projects lists in JSON format')
    list_parser.add_argument('-p', '--project', action='store_true', help='List projects')
    list_parser.add_argument('-f', '--files', action='store_true', help='List files')
    list_parser.add_argument('-dp', '--data-provider', action='store_true', help='List data providers')
    # File filtering options
    list_parser.add_argument('--group_id', type=int, help='Filter files by group ID')
    list_parser.add_argument('--data_provider_id', type=int, help='Filter files by data provider ID')
    list_parser.add_argument('--user_id', type=int, help='Filter files by user ID')
    list_parser.add_argument('--parent_id', type=int, help='Filter files by parent ID')
    list_parser.add_argument('--file_type', type=str, help='Filter files by type')
     
    # Show command
    show_parser = subparsers.add_parser('show', help='Show file or tool details')
    show_parser.add_argument('-f', '--file', type=int, metavar='FILE_ID', help='Show file details for the specified file ID')
    show_parser.add_argument('--tool', action='store_true', help='Show tool details')
    show_parser.add_argument('-id', '--id', type=int, metavar='ID', help='Show specific by ID')
    show_parser.add_argument('--data-provider', action='store_true', help='Show data provider details')

    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload a file to CBRAIN')
    upload_parser.add_argument('--data-provider', type=int, required=True, help='Data provider ID')
    upload_parser.add_argument('--group-id', type=int, default=2, help='Group ID (default: 2)')
    upload_parser.add_argument('--TextFile', action='store_const', const='TextFile', dest='file_type', help='Upload as TextFile')
    upload_parser.add_argument('--SingleFile', action='store_const', const='SingleFile', dest='file_type', help='Upload as SingleFile')
    upload_parser.add_argument('--FileCollection', action='store_const', const='FileCollection', dest='file_type', help='Upload as FileCollection')
    upload_parser.add_argument('file_path', help='Path to the file to upload')
    upload_parser.set_defaults(func=handle_errors(upload_file))

    # MARK: Setup CLI
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 
    if args.command == 'login':
        return handle_errors(create_session)(args)

    if is_authenticated():
        if args.command == 'logout':
            return handle_errors(logout_session)(args) 
        elif args.command == 'whoami':
            return handle_errors(whoami_user)(args)
        elif args.command == 'list':
            if args.project:
                return handle_errors(list_projects)(args)
            elif args.files:
                return handle_errors(list_files)(args)
            elif args.data_provider:
                return handle_errors(list_data_providers)(args)
            else:
                list_parser.print_help()
                return 1
        elif args.command == 'show':
            if args.file:
                return handle_errors(show_file)(args)
            elif args.tool:
                return handle_errors(show_tool)(args)
            elif args.data_provider:
                return handle_errors(show_data_provider)(args)
            else:
                show_parser.print_help()
                return 1
        elif args.command == 'upload':
            return handle_errors(upload_file)(args)
             
 
        if hasattr(args, 'func'):
            return args.func(args)

if __name__ == '__main__':
    sys.exit(main()) 
