from functools import update_wrapper
import json
from fotahubclient.app_updater import AppUpdater

from fotahubclient.base_describer import ArtifactKind
from fotahubclient.base_describer import PascalCaseJSONEncoder
from fotahubclient.os_updater import OSUpdater

class InstalledArtifactInfo(object):

    def __init__(self, name, kind, installed_revision, rollback_revision=None):
        self.name = name
        self.kind = kind
        self.installed_revision = installed_revision
        self.rollback_revision = rollback_revision

class InstalledArtifacts(object):

    def __init__(self, installed_artifacts):
        self.installed_artifacts = installed_artifacts

class InstalledArtifactsDescriber(object):

    def __init__(self, config):
        self.config = config

    def describe(self, artifact_names=[]):
        installed_artifacts = InstalledArtifacts([
            [self.describe_installed_os()] if self.config.os_distro_name in artifact_names else [] +
            self.describe_installed_apps(artifact_names)
        ])
        return json.dumps(installed_artifacts, indent=4, cls=PascalCaseJSONEncoder)

    def describe_installed_os(self):
        os_updater = OSUpdater(self.config.os_distro_name)
        return InstalledArtifactInfo(
            os_updater.os_distro_name, 
            ArtifactKind.OperatingSystem, 
            os_updater.get_installed_os_revision(),
            os_updater.get_rollback_os_revision()
        )

    def describe_installed_apps(self, artifact_names=[]):
        app_updater = AppUpdater(self.config.app_ostree_home)
        return [
            InstalledArtifactInfo(
                name, 
                ArtifactKind.Application, 
                app_updater.resolve_installed_revision(name)
                # TODO Add rollback revision
            ) 
            for name in app_updater.list_app_names() if name in artifact_names]