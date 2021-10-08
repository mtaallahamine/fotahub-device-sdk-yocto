import argparse
import sys
import os
import traceback

from fotahubclient.config_loader import ConfigLoader
import fotahubclient.cli.command_interpreter as commands
from fotahubclient.cli.command_interpreter import CommandInterpreter
from fotahubclient.cli.command_help_formatter import CommandHelpFormatter
from fotahubclient.cli.command_help_formatter import set_command_parser_titles

def cli():
    cli_parser = argparse.ArgumentParser(os.path.basename(sys.argv[0]), description='Update operating system or selected applications on Linux-based IoT edge devices.', formatter_class=CommandHelpFormatter)
    set_command_parser_titles(cli_parser)
    cli_parser.add_argument('-v', '--verbose', action='store_true', default=False, help='enable verbose output')
    cmds = cli_parser.add_subparsers(dest='command')

    update_os_cmd_parser = cmds.add_parser(commands.UPDATE_OPERATING_SYSTEM_CMD, help='update operating system', formatter_class=CommandHelpFormatter)
    set_command_parser_titles(update_os_cmd_parser)
    update_os_cmd_parser.add_argument('-r', '--revision', required=True, help='operating system revision to update to')
    update_os_cmd_parser.add_argument('--max_reboot_failures', default=3, help='maximum number of reboot failures before reverting operating system update')
    
    update_app_cmd_parser = cmds.add_parser(commands.UPDATE_APPLICATION_CMD, help='update an application', formatter_class=CommandHelpFormatter)
    set_command_parser_titles(update_app_cmd_parser)
    update_app_cmd_parser.add_argument('-n', '--name', required=True, help='name of application to be updated')
    update_app_cmd_parser.add_argument('-r', '--revision', required=True, help='application revision to update to')

    update_status_cmd_parser = cmds.add_parser(commands.DESCRIBE_UPDATE_STATUS_CMD, help='retrieve update status', formatter_class=CommandHelpFormatter)
    set_command_parser_titles(update_status_cmd_parser)

    # Show help when no arguments are supplied
    if len(sys.argv) == 1:
        cli_parser.print_help()
        sys.exit(0)

    return cli_parser.parse_args()

def main():
    args = cli()
    
    try:
        config_loader = ConfigLoader(verbose=args.verbose)
        config_loader.load_config()

        command_interpreter = CommandInterpreter(config_loader.os_distro_name)
        command_interpreter.run(args)
    except Exception as err:
        if args.verbose:
            print(''.join(traceback.format_exception(type(err), err, err.__traceback__)), file=sys.stderr)
        else:
            print('ERROR: ' + str(err), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()