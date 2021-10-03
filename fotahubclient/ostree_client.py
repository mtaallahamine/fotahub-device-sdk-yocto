import gi
gi.require_version("OSTree", "1.0")

import logging
from gi.repository import OSTree, GLib

class OSTreeError(Exception):
    pass

class OSTreeClient(object):

    def __init__(self):
        self.logger = logging.getLogger()

        self.ostree_repo = None

    def add_ostree_remote(self, name, url, gpg_verify):
        if not name in self.ostree_repo.remote_list():
            self.logger.info(
                "Adding remote '{}' for {} to local OSTree repo".format(name, url))

            try:
                opts = GLib.Variant(
                    'a{sv}', {'gpg-verify': GLib.Variant('b', gpg_verify)})
                self.ostree_repo.remote_add(
                    name, url, opts, None)
            except GLib.Error as err:
                raise OSTreeError("Failed to add remote '{}' to local OSTree repo".format(
                    name)) from err

    def pull_ostree_revision(self, remote_name, branch_name, revision, depth):
        self.logger.info(
            "Pulling revision '{}' from OSTree remote '{}'".format(revision, remote_name))

        try:
            progress = OSTree.AsyncProgress.new()
            progress.connect(
                'changed', OSTree.Repo.pull_default_console_progress_changed, None)

            opts = GLib.Variant('a{sv}', {'flags': GLib.Variant('i', OSTree.RepoPullFlags.NONE),
                                          'refs': GLib.Variant('as', (branch_name,)),
                                          'override-commit-ids': GLib.Variant('as', (revision,)),
                                          'depth': GLib.Variant('i', depth)})
            result = self.ostree_repo.pull_with_options(
                remote_name, opts, progress, None)

            progress.finish()
            if not result:
                raise OSTreeError("Failed to pull revision '{}' from OSTree remote '{}'".format(
                    revision, remote_name))
        except GLib.Error as err:
            raise OSTreeError("Failed to pull revision '{}' from OSTree remote '{}'".format(
                revision, remote_name)) from err
