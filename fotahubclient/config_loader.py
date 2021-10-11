from pathlib import Path
from configparser import ConfigParser

CONFIG_PATH_DEFAULT = '/etc/fotahub/fotahub.config'
UPDATE_STATUS_PATH_DEFAULT = '/var/log/fotahub/updatestatus.json'

class ConfigLoader(object):
    
    def __init__(self, config_path=CONFIG_PATH_DEFAULT, update_status_path=UPDATE_STATUS_PATH_DEFAULT, verbose=False, stacktrace=False):
        self.config_path = config_path
        self.update_status_path = update_status_path
        
        self.gpg_verify = False
        
        self.verbose = verbose
        self.stacktrace = stacktrace

        self.os_distro_name = None
        self.self_test_command = None

    def load(self):
        config_path = Path(self.config_path)
        if not config_path.is_file():
            raise FileNotFoundError("FotaHub client configuration file '{}' does not exist".format(config_path))
        config = ConfigParser()
        config.read(config_path)

        if config['general'].getboolean('gpg.verify', fallback=False):
            self.gpg_verify = True

        self.update_status_path = config.get('general', 'updates.status.path', fallback=UPDATE_STATUS_PATH_DEFAULT)

        if config['general'].getboolean('verbose', fallback=False):
            self.verbose = True
        if config['general'].getboolean('stacktrace', fallback=False):
            self.stacktrace = True

        self.os_distro_name = config['os'].get('os.distro.name', fallback='os')
        self.self_test_command = config['os'].get('self.test.command')

        self.app_ostree_home = config['app'].get('app.ostree.home')