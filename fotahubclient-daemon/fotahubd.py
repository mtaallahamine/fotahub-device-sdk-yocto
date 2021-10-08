import argparse
import sys
import os
import traceback

from distutils.util import strtobool

from fotahubclient.config_loader import ConfigLoader
from fotahubclient.os_update_finalizer import OSUpdateFinalizer

def cli():
    cli_parser = argparse.ArgumentParser(os.path.basename(sys.argv[0]), description='Handle automatic confirmation or rollback of operating system updates on Linux-based IoT edge devices.')
    cli_parser.add_argument('-c', '--config', dest='config_path', help="path to service configuration file")

    # Show help when no arguments are supplied
    if len(sys.argv) == 1:
        cli_parser.print_help()
        sys.exit(0)

    return cli_parser.parse_args()

def main():
    args = cli()

    try:
        config_loader = ConfigLoader(config_path=args.config_path)
        config_loader.load_config()

        os_update_finalizer = OSUpdateFinalizer(config_loader.self_test_command)
        os_update_finalizer.run()
    except Exception as err:
        if args.verbose:
            print(''.join(traceback.format_exception(type(err), err, err.__traceback__)), file=sys.stderr)
        else:
            print('ERROR: ' + str(err), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()