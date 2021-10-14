import logging

from fotahubclient.os_updater import OSUpdater
from fotahubclient.os_update_finalizer import OSUpdateFinalizer
from fotahubclient.json_object_types import UpdateStatus
from fotahubclient.update_status_tracker import UpdateStatusTracker
from fotahubclient.update_status_tracker import UpdateStatusDescriber
from fotahubclient.installed_artifacts_describer import InstalledArtifactsDescriber

UPDATE_OPERATING_SYSTEM_CMD = 'update-operating-system'
REVERT_OPERATING_SYSTEM_CMD = 'revert-operating-system'
FINISH_OPERATING_SYSTEM_CHANGE_CMD = 'finish-operating-system-change'
UPDATE_APPLICATION_CMD = 'update-application'
REVERT_APPLICATION_CMD = 'revert-application'
DESCRIBE_INSTALLED_ARTIFACTS_CMD = 'describe-installed-artifacts'
DESCRIBE_UPDATE_STATUS_CMD = 'describe-update-status'

class CommandInterpreter(object):

    def __init__(self, config):
        self.logger = logging.getLogger()
        self.config = config

    def run(self, args):
        if args.command == UPDATE_OPERATING_SYSTEM_CMD:
            self.update_operating_system(args.revision, args.max_reboot_failures)
        elif args.command == REVERT_OPERATING_SYSTEM_CMD:
            self.revert_operating_system()
        elif args.command == FINISH_OPERATING_SYSTEM_CHANGE_CMD:
            self.finish_operating_system_change()
        elif args.command == UPDATE_APPLICATION_CMD:
            self.update_application(args.name, args.revision)
        elif args.command == REVERT_APPLICATION_CMD:
            self.revert_application(args.name)
        elif args.command == DESCRIBE_INSTALLED_ARTIFACTS_CMD:
            self.describe_installed_artifacts(args.artifact_names)
        elif args.command == DESCRIBE_UPDATE_STATUS_CMD:
            self.describe_update_status(args.artifact_names)

    def update_operating_system(self, revision, max_reboot_failures):
        self.logger.info('Initiating OS update to revision ' + revision)

        with UpdateStatusTracker(self.config) as tracker:
            updater = OSUpdater(self.config.os_distro_name, self.config.gpg_verify)
            try:
                updater.pull_os_update(revision)
                tracker.record_os_update_status(UpdateStatus.downloaded, revision=revision)

                updater.activate_os_update(revision, max_reboot_failures)
            except Exception as err:
                tracker.record_os_update_status(UpdateStatus.failed, error_message=str(err))
                raise err

    def revert_operating_system(self):
        self.logger.info('Reverting OS to previous revision')
        updater = OSUpdater(self.config.os_distro_name, self.config.gpg_verify)
        updater.revert_os_update()

    def finish_operating_system_change(self):
        self.logger.info('Finalizing OS update or rollback, if any such has happened')

        finalizer = OSUpdateFinalizer(self.config)
        finalizer.run()

    def update_application(self, name, revision):
        self.logger.info('Updating ' + name + ' application to revision ' + revision)
        raise ValueError('Not yet implemented')

    def revert_application(self, name):
        self.logger.info('Reverting ' + name + ' application to previous revision ')
        raise ValueError('Not yet implemented')

    def describe_installed_artifacts(self, artifact_names=[]):
        self.logger.info('Retrieving installed artifacts')

        describer = InstalledArtifactsDescriber(self.config)
        print(describer.describe(artifact_names))

    def describe_update_status(self, artifact_names=[]):
        self.logger.info('Retrieving update status')

        describer = UpdateStatusDescriber(self.config)
        print(describer.describe(artifact_names))
