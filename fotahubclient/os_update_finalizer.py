import subprocess
import logging
import shlex

from fotahubclient.os_updater import OSUpdater

class OSUpdateFinalizer(object):

    def __init__(self, config):
        self.logger = logging.getLogger()
        self.config = config

    def run(self):
        updater = OSUpdater(self.config.os_distro_name, self.config.gpg_verify)
        self.logger.info("Booted OS revision: {}".format(updater.get_installed_os_revision()))
        
        if updater.is_activating_os_update():
            if self.run_self_test():
                updater.confirm_os_update()
            else:
                updater.revert_os_update()
        elif updater.is_reverting_os_update():
            updater.discard_os_update()
        else:
            self.logger.info('No OS update or rollback in progress, nothing to do')

    def run_self_test(self):
        if self.config.self_test_command is not None:
            logging.getLogger().info('Running build-in self test')
            process = subprocess.run(shlex.split(self.config.self_test_command), universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if process.returncode == 0:
                message = 'Build-in self test succeeded'
                if process.stdout:
                    message += ': ' + process.stdout.strip()
                self.logger.info(message)
                return True
            else:
                message = 'Build-in self test failed'
                if process.stderr:
                    message += ': ' + process.stderr.strip()
                elif process.stdout:
                    message += ': ' + process.stdout.strip()
                self.logger.error(message)
                return False