from pydbus import SystemBus
from gi.repository import OSTree, GLib
from fotahubclient import OSTreeClient
from fotahubclient import OSTreeError
import subprocess
import gi

gi.require_version("OSTree", "1.0")

OSTREE_REMOTE_NAME = 'os'
OSTREE_REMOTE_URL = 'https://ostree.fotahub.com'
OSTREE_REMOTE_GPG_VERIFY = False
OSTREE_PULL_DEPTH = 1

class UBootError(Exception):
    pass

class OSUpdater(OSTreeClient):

    def __init__(self):
        super(OSUpdater, self).__init__()

        self.sysroot = None

        self.open_ostree_repo()
        self.add_ostree_remote(OSTREE_REMOTE_NAME, OSTREE_REMOTE_URL, OSTREE_REMOTE_GPG_VERIFY)
    
    def open_ostree_repo(self):
        self.sysroot = OSTree.Sysroot.new_default()
        self.sysroot.load(None)
        self.sysroot.cleanup(None)

        [_, repo] = self.sysroot.get_repo()
        self.ostree_repo = repo

    def pull_os_update(self, revision):
        self.pull_ostree_revision(OSTREE_REMOTE_NAME, revision, OSTREE_PULL_DEPTH)
        self.stage_os_update(revision)

    def stage_os_update(self, revision):
        self.logger.info(
            "Staging OS update with revision {} so that it becomes active after next reboot".format(revision))

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
                raise OSTreeError("Failed to stage OS update with revision {}".format(revision))
        except GLib.Error as err:
            raise OSTreeError("Failed to stage OS update with revision {}".format(revision)) from err

    def activate_os_update(self):
        self.delete_uboot_init_var()
        self.write_os_update_activation_info()
        self.reboot()

    def is_activating_os_update(self):
        self.logger.info("Checking if an OS update is in progress")

    def is_os_update_reverted(self):
        self.logger.info("Checking if latest OS update has been reverted")

    def write_os_update_activation_info(self):
        self.logger.info("Writing OS update activation info")

    def read_os_update_activation_info(self):
        self.logger.info("Reading OS update activation info")

    def delete_os_update_activation_info(self):
        self.logger.info("Deleting OS update activation info")
    
    def reboot(self):
        self.logger.info("Rebooting system to activate staged OS update")
        
        try:
            subprocess.run("reboot")
        except subprocess.CalledProcessError as err:
            raise OSError("Failed to reboot system") from err

    def delete_uboot_init_var(self):
        self.logger.info("Deleting U-Boot environment variable 'init_var' to trigger rollback procedure")
        
        try:
            subprocess.run(["fw_setenv", "init_var"], check=True)
        except subprocess.CalledProcessError as err:
            raise UBootError("Failed to delete U-Boot environment variable 'init_var'") from err

    def set_uboot_success_var(self):
        self.logger.info("Setting U-Boot environment variable 'success' to flag activated OS update successful")

        try:
            subprocess.run(["fw_setenv", "success", "1"], check=True)
        except subprocess.CalledProcessError as err:
            raise UBootError("Failed to set U-Boot environment variable 'success'") from err
