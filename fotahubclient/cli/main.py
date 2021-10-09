import argparse
import sys
import os
import logging
import traceback

import fotahubclient.config_loader as config_loader
import fotahubclient.cli.command_interpreter as commands
import fotahubclient.os_updater as os_updater
from fotahubclient.config_loader import ConfigLoader
from fotahubclient.cli.command_interpreter import CommandInterpreter
from fotahubclient.cli.command_help_formatter import CommandHelpFormatter
from fotahubclient.cli.command_help_formatter import set_command_parser_titles

LOG_MESSAGE_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def cli():
    cli = argparse.ArgumentParser(os.path.basename(sys.argv[0]), description='Manage updates of operating system or selected applications on Linux-based IoT edge devices.', formatter_class=CommandHelpFormatter)
    set_command_parser_titles(cli)
    cli.add_argument('-c', '--config', dest='config_path', default=config_loader.CONFIG_PATH_DEFAULT, help='path to configuration file (optional, defaults to ' + config_loader.CONFIG_PATH_DEFAULT + ')')
    cli.add_argument('-v', '--verbose', action='store_true', default=False, help='enable verbose output (optional, disabled by default)')
    cli.add_argument('-s', '--stacktrace', action='store_true', default=False, help='enable output of stacktrace for exceptions (optional, disabled by default)')
    cmds = cli.add_subparsers(dest='command')

    cmd = cmds.add_parser(commands.START_OPERATING_SYSTEM_UPDATE_CMD, help='initiate operating system update (involves reboot)', formatter_class=CommandHelpFormatter)
    set_command_parser_titles(cmd)
    cmd.add_argument('-r', '--revision', required=True, help='operating system revision to update to')
    cmd.add_argument('--max_reboot_failures', default=os_updater.MAX_REBOOT_FAILURES_DEFAULT, help='maximum number of reboot failures before reverting operating system update (optional, defaults to ' + str(os_updater.MAX_REBOOT_FAILURES_DEFAULT) + ')')
    
    cmd = cmds.add_parser(commands.FINISH_OPERATING_SYSTEM_UPDATE_CMD, help='finalize operating system update (after reboot)', formatter_class=CommandHelpFormatter)
    set_command_parser_titles(cmd)

    cmd = cmds.add_parser(commands.REVERT_OPERATING_SYSTEM_CMD, help='revert operating system to previous revision', formatter_class=CommandHelpFormatter)
    set_command_parser_titles(cmd)

    cmd = cmds.add_parser(commands.UPDATE_APPLICATION_CMD, help='update an application', formatter_class=CommandHelpFormatter)
    set_command_parser_titles(cmd)
    cmd.add_argument('-n', '--name', required=True, help='name of application to be updated')
    cmd.add_argument('-r', '--revision', required=True, help='application revision to update to')

    cmd = cmds.add_parser(commands.REVERT_APPLICATION_CMD, help='revert an application to previous revision', formatter_class=CommandHelpFormatter)
    set_command_parser_titles(cmd)
    cmd.add_argument('-n', '--name', required=True, help='name of application to be reverted')

    cmd = cmds.add_parser(commands.DESCRIBE_INSTALLED_ARTIFACTS_CMD, help='retrieve installed artifacts', formatter_class=CommandHelpFormatter)
    set_command_parser_titles(cmd)
    cmd.add_argument('-n', '--artifact-names', metavar='ARTIFACT_NAME', nargs='*', default=[], help='names of artifacts to consider (optional, defaults to all artifacts)')

    cmd = cmds.add_parser(commands.DESCRIBE_UPDATE_STATUS_CMD, help='retrieve update status', formatter_class=CommandHelpFormatter)
    set_command_parser_titles(cmd)
    cmd.add_argument('-n', '--artifact-names', metavar='ARTIFACT_NAME', nargs='*', default=[], help='names of artifacts to consider (defaults to all artifacts)')

    # Show help when no arguments are supplied
    if len(sys.argv) == 1:
        cli.print_help()
        sys.exit(0)

    return cli.parse_args()

def main():
    args = cli()
    
    try:
        config = ConfigLoader(args.config_path, args.verbose, args.stacktrace)
        config.load()

        log_level = logging.INFO if config.verbose else logging.WARNING
        logging.basicConfig(stream=sys.stdout, level=log_level, format=LOG_MESSAGE_FORMAT, datefmt=LOG_DATE_FORMAT)

        command_interpreter = CommandInterpreter(config.os_distro_name, config.self_test_command)
        command_interpreter.run(args)
    except Exception as err:
        if config.stacktrace:
            print(''.join(traceback.format_exception(type(err), err, err.__traceback__)), file=sys.stderr)
        else:
            print('ERROR: ' + str(err), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()