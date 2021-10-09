import sys
import os
import logging
from pathlib import Path

from distutils.util import strtobool
from configparser import ConfigParser

CONFIG_PATH_DEFAULT = '/etc/fotahub/fotahubclient.cfg'

class ConfigLoader(object):
    
    def __init__(self, config_path=CONFIG_PATH_DEFAULT, verbose=False, stacktrace=False):
        self.config_path = config_path
        
        self.verbose = verbose
        self.stacktrace = stacktrace

        self.os_distro_name = None
        self.self_test_command = None

    def load(self):
        config_path = Path(self.config_path)
        if not config_path.is_file():
            raise FileNotFoundError("FotaHub client configuration file '{}' does not exist".format(config_path))
        parser = ConfigParser()
        parser.read_file(config_path.open())

        if strtobool(parser.get('general', 'verbose')): 
            self.verbose = True
        if strtobool(parser.get('general', 'stacktrace')): 
            self.stacktrace = True

        self.os_distro_name = parser.get('os', 'operating.system.distribution.name', fallback='os')
        self.self_test_command = parser.get('os', 'self.test.command')