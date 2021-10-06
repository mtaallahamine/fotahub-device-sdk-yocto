import gi
gi.require_version("OSTree", "1.0")

from pydbus import SystemBus
from gi.repository import OSTree, GLib
import subprocess
from fotahubclient.ostree_client import OSTreeClient
from fotahubclient.ostree_client import OSTreeError
from fotahubclient.uboot_operator import UBootOperator

OSTREE_REMOTE_NAME = 'fotahub'
OSTREE_REMOTE_URL = 'https://ostree.fotahub.com'
OSTREE_REMOTE_GPG_VERIFY = False
OSTREE_PULL_DEPTH = 1

UBOOT_FLAG_ACTIVATING_OS_UPDATE = 'acivating_os_update'
UBOOT_FLAG_REVERTING_OS_UPDATE = 'reverting_os_update'
UBOOT_VAR_OS_UPDATE_BOOT_FAILURE_CREDIT = 'os_update_boot_failure_credit'

class OSUpdater(OSTreeClient, UBootOperator):

    def __init__(self):
        super(OSUpdater, self).__init__()

        self.sysroot = None

        self.open_ostree_repo()

        if not self.has_ostree_remote(OSTREE_REMOTE_NAME):
            self.add_ostree_remote(OSTREE_REMOTE_NAME, OSTREE_REMOTE_URL, OSTREE_REMOTE_GPG_VERIFY)
    
    def open_ostree_repo(self):
        self.sysroot = OSTree.Sysroot.new_default()
        self.sysroot.load(None)
        self.sysroot.cleanup(None)

        [_, repo] = self.sysroot.get_repo()
        self.ostree_repo = repo

    def get_booted_os_revision(self):
        return self.sysroot.get_booted_deployment().get_csum()
        
    def pull_os_update(self, branch_name, revision):
        self.pull_ostree_revision(OSTREE_REMOTE_NAME, branch_name, revision, OSTREE_PULL_DEPTH)
        self.stage_os_update(revision)

    def stage_os_update(self, revision):
        self.logger.info(
            "Staging OS update with revision '{}' so that it becomes active after next reboot".format(revision))

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

    def activate_os_update(self, max_boot_failure_count):
        self.logger.info("Activating staged OS update")
        self.set_uboot_env_var(UBOOT_FLAG_ACTIVATING_OS_UPDATE, '1')
        self.set_uboot_env_var(UBOOT_VAR_OS_UPDATE_BOOT_FAILURE_CREDIT, str(max_boot_failure_count))
        self.reboot()

    def is_activating_os_update(self):
        self.logger.info("Checking if an OS update is about to be activated")
        return self.isset_uboot_env_var(UBOOT_FLAG_ACTIVATING_OS_UPDATE)

    def confirm_os_update(self):
        self.logger.info("Confirming activated OS update")
        self.set_uboot_env_var(UBOOT_FLAG_ACTIVATING_OS_UPDATE)
        self.set_uboot_env_var(UBOOT_VAR_OS_UPDATE_BOOT_FAILURE_CREDIT)

    def has_os_update_reverted(self, revision):
        self.logger.info("Checking if OS update has reverted to previously installed revision")
        return self.get_booted_os_revision() != revision

    def cleanup_reverted_os_update(self):
        try:
            [pending, _] = self.sysroot.query_deployments_for(None)
            if pending is not None:
                self.logger.info(
                    "Cleaning up reverted OS update with revision '{}'".format(pending.get_csum()))
                    
                # 0 is the index of the pending deployment
                # TODO Reimplement this behavior using OSTree API (see https://github.com/ostreedev/ostree/blob/8cb5d920c4b89d17c196f30f2c59fcbd4c762a17/src/ostree/ot-admin-builtin-undeploy.c#L59)
                subprocess.run(["ostree", "admin", "undeploy", "0"], check=True)
        except subprocess.CalledProcessError as err:
            raise OSTreeError("Failed to undeploy reverted OS update") from err

    def revert_os_update(self):
        self.logger.info("Reverting activated OS update")
        self.set_uboot_env_var(UBOOT_FLAG_REVERTING_OS_UPDATE, '1')
        self.reboot()
