import os
import subprocess

import gi
gi.require_version("OSTree", "1.0")
from gi.repository import OSTree, GLib, Gio
from pydbus import SystemBus

import fotahubclient.common_constants as constants
from fotahubclient.ostree_repo import OSTreeRepo
from fotahubclient.ostree_repo import OSTreeError

MAX_REBOOT_FAILURES_DEFAULT = 3

class AppUpdater(OSTreeRepo):

    def __init__(self, repo_path):
        super(AppUpdater, self).__init__()

        self.__open_ostree_repo(repo_path)

        if not self.has_ostree_remote(constants.OSTREE_REMOTE_NAME):
            self.add_ostree_remote(constants.OSTREE_REMOTE_NAME, constants.OSTREE_REMOTE_URL, constants.OSTREE_REMOTE_GPG_VERIFY)

        system_bus = SystemBus()
        self.systemd = system_bus.get('.systemd1')

    def __open_ostree_repo(self, repo_path):
        try:
            self.ostree_repo = OSTree.Repo.new(Gio.File.new_for_path(repo_path))
            if os.path.exists(repo_path):
                self.logger.info("Opening application OSTree repo located at '{}'".format(repo_path))
                self.ostree_repo.open(None)
            else:
                self.logger.info("Creating and opening new application OSTree repo ocated at '{}'".format(repo_path))
                self.ostree_repo.create(OSTree.RepoMode.BARE_USER_ONLY, None)
        except GLib.Error as err:
            raise OSTreeError('Failed to open application OSTree repo') from err

    def list_app_names(self):
        return self.list_ostree_refs()

    def resolve_installed_revision(self, app_name):
        return self.resolve_ostree_revision(app_name)