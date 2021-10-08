import subprocess
import logging

from fotahubclient.os_updater import OSUpdater

class OSUpdateFinalizer(object):

    def __init__(self, self_test_command=None):
        self.logger = logging.getLogger()
        self.self_test_command = self_test_command

    def run(self):
        updater = OSUpdater()
        self.logger.info("Booted OS revision: {}".format(updater.get_booted_os_revision()))
        
        if updater.is_activating_os_update():
            if not updater.is_reverting_os_update():
                if self.run_self_test():
                    updater.confirm_os_update()
                else:
                    updater.revert_os_update()
            else:
                updater.remove_os_update()

    def run_self_test(self):
        if self.self_test_command is not None:
            logging.getLogger().info('Running build-in self test')
            process = subprocess.run(self.self_test_command, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if process.returncode:
                self.logger.info('Build-in self test succeeded')
                return True
            else:
                error_message = 'Build-in self test failed'
                if process.stderr:
                    error_message += ': ' + process.stderr
                elif process.stdout:
                    error_message += ': ' + process.stdout
                self.logger.error(error_message)
                return False