import sys
import os
import logging

from distutils.util import strtobool
from configparser import ConfigParser

DEFAULT_CONFIG_PATH = '/etc/fotahub/fotahubclient.cfg'

LOG_MESSAGE_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

class ConfigLoader(object):
    
    def __init__(self, config_path=DEFAULT_CONFIG_PATH, verbose=False):
        self.config_path = config_path
        self.verbose = verbose

        self.os_distro_name = None
        self.self_test_command = None

    def load_config(self):
        config_path = os.path.Path(self.config_path)
        if not config_path.is_file():
            raise FileNotFoundError("FotaHub client configuration file '{}' does not exist".format(config_path.name), file=sys.stderr)
        config_parser = ConfigParser()
        config_parser.read_file(config_path.open())

        if self.verbose or strtobool(config_parser.get('general', 'verbose')):
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=LOG_MESSAGE_FORMAT, datefmt=LOG_DATE_FORMAT)
        else:
            logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_MESSAGE_FORMAT, datefmt=LOG_DATE_FORMAT)

        self.os_distro_name = config_parser.get('os', 'operating.system.distribution.name', fallback='os')
        self.self_test_command = config_parser.get('os', 'self.test.command')