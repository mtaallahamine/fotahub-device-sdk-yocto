import logging

from fotahubclient.os_updater import OSUpdater
from fotahubclient.os_update_finalizer import OSUpdateFinalizer
from fotahubclient.update_status_describer import UpdateStatusDescriber
from fotahubclient.installed_artifacts_describer import InstalledArtifactsDescriber

START_OPERATING_SYSTEM_UPDATE_CMD = 'start-operating-system-update'
FINISH_OPERATING_SYSTEM_UPDATE_CMD = 'finish-operating-system-update'
REVERT_OPERATING_SYSTEM_CMD = 'revert-operating-system'
UPDATE_APPLICATION_CMD = 'update-application'
REVERT_APPLICATION_CMD = 'revert-application'
DESCRIBE_INSTALLED_ARTIFACTS_CMD = 'describe-installed-artifacts'
DESCRIBE_UPDATE_STATUS_CMD = 'describe-update-status'

class CommandInterpreter(object):

    def __init__(self, config):
        self.logger = logging.getLogger()
        self.config = config

    def run(self, args):
        if args.command == START_OPERATING_SYSTEM_UPDATE_CMD:
            self.start_operating_system_update(args.revision, args.max_reboot_failures)
        elif args.command == FINISH_OPERATING_SYSTEM_UPDATE_CMD:
            self.finish_operating_system_update()
        elif args.command == REVERT_OPERATING_SYSTEM_CMD:
            self.revert_operating_system()
        elif args.command == UPDATE_APPLICATION_CMD:
            self.update_application(args.name, args.revision)
        elif args.command == REVERT_APPLICATION_CMD:
            self.revert_application(args.name)
        elif args.command == DESCRIBE_INSTALLED_ARTIFACTS_CMD:
            self.describe_installed_artifacts(args.artifact_names)
        elif args.command == DESCRIBE_UPDATE_STATUS_CMD:
            self.describe_update_status(args.artifact_names)

    def start_operating_system_update(self, revision, max_reboot_failures):
        self.logger.info('Initiating operating system update to revision ' + revision)

        updater = OSUpdater(self.config.os_distro_name)
        updater.pull_os_update(revision)
        updater.activate_os_update(revision, max_reboot_failures)

    def finish_operating_system_update(self):
        self.logger.info('Finalizing operating system update')

        finalizer = OSUpdateFinalizer(self.config)
        finalizer.run()

    def revert_operating_system(self):
        self.logger.info('Reverting operating system to previous revision')
        raise ValueError('Not yet implemented')

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
