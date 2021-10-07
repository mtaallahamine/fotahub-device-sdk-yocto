import argparse
import sys

class CustomHelpFormatter(argparse.HelpFormatter):
    def _format_action(self, action):
        if type(action) == argparse._SubParsersAction:
            # Inject new class variable for subcommand formatting
            subactions = action._get_subactions()
            invocations = [self._format_action_invocation(a) for a in subactions]
            self._subcommand_max_length = max(len(i) for i in invocations)

        if type(action) == argparse._SubParsersAction._ChoicesPseudoAction:
            # Format subcommand help line
            subcommand = self._format_action_invocation(action)
            width = self._subcommand_max_length
            help_text = ""
            if action.help:
                help_text = self._expand_help(action)
            return "  {:{width}} -  {}\n".format(subcommand, help_text, width=width)

        elif type(action) == argparse._SubParsersAction:
            # Process subcommand help section
            msg = '\n'
            for subaction in action._get_subactions():
                msg += self._format_action(subaction)
            return msg
        else:
            return super(CustomHelpFormatter, self)._format_action(action)

def cli():
    cli = argparse.ArgumentParser('fotahub', description='Update operating system or selected applications on Linux-based IoT edge devices.', formatter_class=CustomHelpFormatter)
    cli._positionals.title = "commands"
    cmds = cli.add_subparsers(dest='command')

    update_os_cmd = cmds.add_parser('update-operating-system', help='update operating system')
    update_os_cmd.add_argument('-r', '--revision', required=True, help='the operating system revision to update to')
    
    update_app_cmd = cmds.add_parser('update-application', help='update an application')
    update_app_cmd.add_argument('-n', '--name', required=True, help='name of application to be updated')
    update_app_cmd.add_argument('-r', '--revision', required=True, help='application revision to update to')

    cmds.add_parser('describe-update-status', help='retrieve update status')

    # Show help when no arguments are supplied
    if len(sys.argv) == 1:
        cli.print_help()
        sys.exit(0)

    args = cli.parse_args()

    if args.command == 'update-operating-system':
        print('Updating operating system to revision ' + args.revision)
    elif args.command == 'update-application':
        print('Updating ' + args.name + ' application to revision ' + args.revision)
    elif args.command == 'describe-update-status':
        print('Retrieving update status')