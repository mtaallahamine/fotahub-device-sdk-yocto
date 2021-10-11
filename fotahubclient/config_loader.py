from pathlib import Path
from distutils.util import strtobool
from configparser import ConfigParser

CONFIG_PATH_DEFAULT = '/etc/fotahub/fotahub.config'
UPDATE_STATUS_PATH_DEFAULT = '/var/log/fotahub/updatestatus.json'

class ConfigLoader(object):
    
    def __init__(self, config_path=CONFIG_PATH_DEFAULT, update_status_path=UPDATE_STATUS_PATH_DEFAULT, verbose=False, stacktrace=False):
        self.config_path = config_path
        self.update_status_path = update_status_path
        
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

        self.update_status_path = parser.get('general', 'updates.status.path', fallback=UPDATE_STATUS_PATH_DEFAULT)

        if strtobool(parser.get('general', 'verbose')): 
            self.verbose = True
        if strtobool(parser.get('general', 'stacktrace')): 
            self.stacktrace = True

        self.os_distro_name = parser.get('os', 'os.distro.name', fallback='os')
        self.self_test_command = parser.get('os', 'self.test.command')

        self.app_ostree_home = parser.get('app', 'app.ostree.home')