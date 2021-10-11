import subprocess

import gi
gi.require_version("OSTree", "1.0")
from gi.repository import OSTree, GLib

import fotahubclient.common_constants as constants
from fotahubclient.ostree_repo import OSTreeRepo
from fotahubclient.ostree_repo import OSTreeError
from fotahubclient.uboot_operator import UBootOperator

OSTREE_SYSTEM_REPOSITORY_PATH = '/ostree/repo'

UBOOT_FLAG_ACTIVATING_OS_UPDATE = 'activating_os_update'
UBOOT_FLAG_REVERTING_OS_UPDATE = 'reverting_os_update'
UBOOT_VAR_OS_UPDATE_REBOOT_FAILURE_CREDIT = 'os_update_reboot_failure_credit'

MAX_REBOOT_FAILURES_DEFAULT = 3

class OSUpdater(OSTreeRepo, UBootOperator):

    def __init__(self, distro_name):
        super(OSUpdater, self).__init__()
        self.distro_name = distro_name

        self.sysroot = None

        self.__open_ostree_repo()

        if not self.has_ostree_remote(constants.OSTREE_REMOTE_NAME):
            self.add_ostree_remote(constants.OSTREE_REMOTE_NAME, constants.OSTREE_REMOTE_URL, constants.OSTREE_REMOTE_GPG_VERIFY)
    
    def __open_ostree_repo(self):
        try:
            self.sysroot = OSTree.Sysroot.new_default()
            self.logger.info("Opening OS OSTree repo located at '{}'".format(OSTREE_SYSTEM_REPOSITORY_PATH))
            self.sysroot.load(None)
            self.sysroot.cleanup(None)

            [_, repo] = self.sysroot.get_repo()
            self.ostree_repo = repo
        except GLib.Error as err:
            raise OSTreeError('Failed to open OS OSTree repo') from err

    def get_installed_os_revision(self):
        return self.sysroot.get_booted_deployment().get_csum()

    def get_rollback_os_revision(self):
        [_, rollback] = self.sysroot.query_deployments_for(None)
        return rollback.get_csum()
        
    def pull_os_update(self, revision):
        self.pull_ostree_revision(constants.OSTREE_REMOTE_NAME, self.distro_name, revision, constants.OSTREE_PULL_DEPTH)

    def __stage_os_update(self, revision):
        self.logger.info(
            "Staging OS update with revision '{}'".format(revision))
        [pending, _] = self.sysroot.query_deployments_for(None)
        if pending is not None:
            raise OSTreeError("Cannot stage any new OS update while some other OS update is still pending")

        try:
            booted_deployment = self.sysroot.get_booted_deployment()
            if booted_deployment is None:
                raise OSTreeError("Currently running system has not been provisioned through OSTree")

            [_, checksum] = self.ostree_repo.resolve_rev(revision, False)
            origin = booted_deployment.get_origin()
            osname = booted_deployment.get_osname()

            [result, _] = self.sysroot.stage_tree(
                osname, checksum, origin, booted_deployment, None, None)
            if not result:
                raise OSTreeError("Failed to stage OS update with revision '{}'".format(revision))
        except GLib.Error as err:
            raise OSTreeError("Failed to stage OS update with revision '{}'".format(revision)) from err

    def activate_os_update(self, revision, max_reboot_failures):
        self.logger.info("Activating OS update")
        if self.is_activating_os_update():
            raise OSTreeError("Cannot activate any new OS update while the activation of some other OS update is still underway")
        if self.is_reverting_os_update():
            raise OSTreeError("Cannot activate any new OS update while the rollback of some other OS update is still underway")
        if revision == self.get_installed_os_revision():
            raise OSTreeError("Cannot perform OS update towards the same revision that is already in use")
            
        self.__stage_os_update(revision)
        self.set_uboot_env_var(UBOOT_FLAG_ACTIVATING_OS_UPDATE, '1')
        self.set_uboot_env_var(UBOOT_VAR_OS_UPDATE_REBOOT_FAILURE_CREDIT, str(max_reboot_failures))
        self.reboot()

    def is_activating_os_update(self):
        self.logger.info("Checking if an OS update is about to be activated")
        return self.isset_uboot_env_var(UBOOT_FLAG_ACTIVATING_OS_UPDATE)

    def confirm_os_update(self):
        self.logger.info("Confirming activated OS update")
        if not self.is_activating_os_update():
            raise OSTreeError("Cannot confirm any OS update when no such has been activated before")

        self.set_uboot_env_var(UBOOT_FLAG_ACTIVATING_OS_UPDATE)
        self.set_uboot_env_var(UBOOT_VAR_OS_UPDATE_REBOOT_FAILURE_CREDIT)

    def revert_os_update(self):
        self.logger.info("Reverting latest OS update")
        self.set_uboot_env_var(UBOOT_FLAG_ACTIVATING_OS_UPDATE)
        self.set_uboot_env_var(UBOOT_VAR_OS_UPDATE_REBOOT_FAILURE_CREDIT)
        self.set_uboot_env_var(UBOOT_FLAG_REVERTING_OS_UPDATE, '1')
        self.reboot()

    def is_reverting_os_update(self):
        self.logger.info("Checking if OS update is about to be reverted")
        return self.isset_uboot_env_var(UBOOT_FLAG_REVERTING_OS_UPDATE)

    def remove_os_update(self):
        self.logger.info("Removing latest OS update")
        if not self.is_reverting_os_update():
            raise OSTreeError("Cannot remove any OS update when no such has been reverted before")
        
        self.set_uboot_env_var(UBOOT_FLAG_REVERTING_OS_UPDATE)
        try:
            [pending, _] = self.sysroot.query_deployments_for(None)
            if pending is not None:                    
                # 0 is the index of the pending deployment
                # TODO Reimplement this behavior using OSTree API (see https://github.com/ostreedev/ostree/blob/8cb5d920c4b89d17c196f30f2c59fcbd4c762a17/src/ostree/ot-admin-builtin-undeploy.c#L59)
                subprocess.run(["ostree", "admin", "undeploy", "0"], check=True)
        except subprocess.CalledProcessError as err:
            raise OSTreeError("Failed to undeploy reverted OS update") from err
