import sys
import logging
import traceback

from fotahubclient.cli.cli import CLI
from fotahubclient.config_loader import ConfigLoader
from fotahubclient.cli.command_interpreter import CommandInterpreter

LOG_MESSAGE_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def main():
    try:
        cli = CLI()
        args = cli.parse_args()
        
        config = ConfigLoader(args.config_path, args.verbose, args.stacktrace)
        config.load()

        log_level = logging.INFO if config.verbose else logging.WARNING
        logging.basicConfig(stream=sys.stdout, level=log_level, format=LOG_MESSAGE_FORMAT, datefmt=LOG_DATE_FORMAT)

        command_interpreter = CommandInterpreter(config)
        command_interpreter.run(args)
    except Exception as err:
        if config.stacktrace:
            print('')
            print(''.join(traceback.format_exception(type(err), err, err.__traceback__)), file=sys.stderr)
        else:
            print('')
            print('ERROR: ' + str(err), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()