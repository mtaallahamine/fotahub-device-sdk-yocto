import logging

from fotahubclient.os_updater import OSUpdater

UPDATE_OPERATING_SYSTEM_CMD = 'update-operating-system'
UPDATE_APPLICATION_CMD = 'update-application'
DESCRIBE_UPDATE_STATUS_CMD = 'describe-update-status'

class CommandInterpreter(object):

    def __init__(self, distro_name):
        self.logger = logging.getLogger()
        self.distro_name = distro_name

    def run(self, args):
        if args.command == UPDATE_OPERATING_SYSTEM_CMD:
            self.update_operating_system(args.revision, args.max_reboot_failures)
        elif args.command == UPDATE_APPLICATION_CMD:
            self.update_application(args.name, args.revision)
        elif args.command == DESCRIBE_UPDATE_STATUS_CMD:
            self.describe_update_status()

    def update_operating_system(self, revision, max_reboot_failures):
        self.logger.debug('Updating ' + self.distro_name + ' operating system to revision ' + revision)
        updater = OSUpdater()
        updater.pull_os_update(self.distro_name, revision)
        updater.activate_os_update(revision, max_reboot_failures)

    def update_application(self, name, revision):
        self.logger.debug('Updating ' + name + ' application to revision ' + revision)
        raise ValueError('Not yet implemented')

    def describe_update_status(self):
        self.logger.debug('Retrieving update status')
        raise ValueError('Not yet implemented')