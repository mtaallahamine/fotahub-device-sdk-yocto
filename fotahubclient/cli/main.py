import argparse
import sys

from fotahubclient.cli.command_help_formatter import CommandHelpFormatter
from fotahubclient.cli.command_help_formatter import set_command_parser_titles
import fotahubclient.cli.commands as commands

def cli():
    cli = argparse.ArgumentParser('fotahub', description='Update operating system or selected applications on Linux-based IoT edge devices.', formatter_class=CommandHelpFormatter)
    set_command_parser_titles(cli)
    cmds = cli.add_subparsers(dest='command')

    update_os_cmd = cmds.add_parser('update-operating-system', help='update operating system', formatter_class=CommandHelpFormatter)
    set_command_parser_titles(update_os_cmd)
    update_os_cmd.add_argument('-r', '--revision', required=True, help='the operating system revision to update to')
    
    update_app_cmd = cmds.add_parser('update-application', help='update an application', formatter_class=CommandHelpFormatter)
    set_command_parser_titles(update_app_cmd)
    update_app_cmd.add_argument('-n', '--name', required=True, help='name of application to be updated')
    update_app_cmd.add_argument('-r', '--revision', required=True, help='application revision to update to')

    update_status_cmd = cmds.add_parser('describe-update-status', help='retrieve update status', formatter_class=CommandHelpFormatter)
    set_command_parser_titles(update_status_cmd)

    # Show help when no arguments are supplied
    if len(sys.argv) == 1:
        cli.print_help()
        sys.exit(0)

    args = cli.parse_args()

    try:
        if args.command == 'update-operating-system':
            commands.update_operating_system(args.revision)
        elif args.command == 'update-application':
            commands.update_application(args.name, args.revision)
        elif args.command == 'describe-update-status':
            commands.describe_update_status()
    except Exception as err:
        print(str(err), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    cli()