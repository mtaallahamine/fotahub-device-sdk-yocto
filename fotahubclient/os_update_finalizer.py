import subprocess
import logging
import shlex

from fotahubclient.os_updater import OSUpdater
from fotahubclient.update_status_tracker import UpdateStatus
from fotahubclient.update_status_tracker import UpdateStatusTracker

class OSUpdateFinalizer(object):

    def __init__(self, config):
        self.logger = logging.getLogger()
        self.config = config

    def run(self):
        with UpdateStatusTracker(self.config) as tracker:
            updater = OSUpdater(self.config.os_distro_name, self.config.gpg_verify)
            self.logger.info("Booted OS revision: {}".format(updater.get_installed_os_revision()))
            
            if updater.is_activating_os_update():
                tracker.record_os_update_status(UpdateStatus.activated)

                [success, message] = self.run_self_test()
                if success:
                    updater.confirm_os_update()
                    tracker.record_os_update_status(UpdateStatus.confirmed)
                else:
                    updater.revert_os_update()
                    tracker.record_os_update_status(UpdateStatus.failed, message)
            
            elif updater.is_reverting_os_update():
                updater.discard_os_update()
                tracker.record_os_update_status(UpdateStatus.reverted)
            
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
                return [True, message]
            else:
                message = 'Build-in self test failed'
                if process.stderr:
                    message += ': ' + process.stderr.strip()
                elif process.stdout:
                    message += ': ' + process.stdout.strip()
                self.logger.error(message)
                return [False, message]
