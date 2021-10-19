import subprocess
import logging
import shlex

from fotahubclient.os_updater import OSUpdater
from fotahubclient.system_helper import run_hook_command
from fotahubclient.update_status_tracker import UpdateStatus
from fotahubclient.update_status_tracker import UpdateStatusTracker

class OSUpdateInitiator(object):

    def __init__(self, config):
        self.logger = logging.getLogger()
        self.config = config

    def initiate_os_update(self, revision, max_reboot_failures):
        with UpdateStatusTracker(self.config) as tracker:
            try:
                updater = OSUpdater(self.config.os_distro_name, self.config.ostree_gpg_verify)
                updater.pull_os_update(revision)
                tracker.record_os_update_status(UpdateStatus.downloaded, revision=revision)

                [success, message] = run_hook_command('OS update verification', self.config.os_update_verification_command, revision)
                if success:
                    tracker.record_os_update_status(UpdateStatus.verified, revision=revision, save_instantly=True)
                    updater.activate_os_update(revision, max_reboot_failures)
                else:
                    raise RuntimeError(message)

            except Exception as err:
                tracker.record_os_update_status(UpdateStatus.failed, revision=revision, message=str(err))
                raise err

class OSUpdateReverter(object):

    def __init__(self, config):
        self.logger = logging.getLogger()
        self.config = config

    def revert_os_update(self):
        with UpdateStatusTracker(self.config) as tracker:
            try:
                updater = OSUpdater(self.config.os_distro_name, self.config.ostree_gpg_verify)
                updater.revert_os_update()
            except Exception as err:
                tracker.record_os_update_status(UpdateStatus.failed, message=str(err))
                raise err

class OSUpdateFinalizer(object):

    def __init__(self, config):
        self.logger = logging.getLogger()
        self.config = config

    def finalize_os_update(self):
        with UpdateStatusTracker(self.config) as tracker:
            try:
                updater = OSUpdater(self.config.os_distro_name, self.config.ostree_gpg_verify)
                self.logger.info("Booted OS revision: {}".format(updater.get_installed_os_revision()))
                
                if updater.is_activating_os_update():
                    tracker.record_os_update_status(UpdateStatus.activated)

                    [success, message] = run_hook_command('OS update self test', self.config.os_update_self_test_command)
                    if success:
                        updater.confirm_os_update()
                        tracker.record_os_update_status(UpdateStatus.confirmed)
                    else:
                        tracker.record_os_update_status(UpdateStatus.failed, message=message)
                        updater.revert_os_update()
                
                elif updater.is_reverting_os_update():
                    updater.discard_os_update()
                    tracker.record_os_update_status(UpdateStatus.reverted)
                
                else:
                    self.logger.info('No OS update or rollback in progress, nothing to do')
            except Exception as err:
                tracker.record_os_update_status(UpdateStatus.failed, message=str(err))
                raise err
