import os
import logging
import subprocess

import gi
gi.require_version("OSTree", "1.0")
from gi.repository import OSTree, GLib, Gio
from pydbus import SystemBus

import fotahubclient.common_constants as constants
from fotahubclient.ostree_repo import OSTreeRepo
from fotahubclient.ostree_repo import OSTreeError

MAX_REBOOT_FAILURES_DEFAULT = 3

class AppUpdater(object):

    def __init__(self, repo_path, gpg_verify):
        self.logger = logging.getLogger()

        self.gpg_verify = gpg_verify

        repo = self.__open_ostree_repo(repo_path)
        self.ostree_repo = OSTreeRepo(repo)
        self.ostree_repo.add_ostree_remote(constants.OSTREE_REMOTE_NAME, constants.OSTREE_REMOTE_URL, self.gpg_verify)

        system_bus = SystemBus()
        self.systemd = system_bus.get('.systemd1')

    def __open_ostree_repo(self, repo_path):
        try:
            repo = OSTree.Repo.new(Gio.File.new_for_path(repo_path))
            if os.path.exists(repo_path):
                self.logger.info("Opening application OSTree repo located at '{}'".format(repo_path))
                repo.open(None)
            else:
                self.logger.info("Creating and opening new application OSTree repo ocated at '{}'".format(repo_path))
                repo.create(OSTree.RepoMode.BARE_USER_ONLY, None)
            return repo
        except GLib.Error as err:
            raise OSTreeError('Failed to open application OSTree repo') from err

    def list_app_names(self):
        return self.ostree_repo.list_ostree_refs()

    def resolve_installed_revision(self, app_name):
        return self.ostree_repo.resolve_ostree_revision(app_name)