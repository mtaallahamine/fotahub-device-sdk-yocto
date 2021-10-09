import json

from fotahubclient.artifact_describer import ArtifactKind
from fotahubclient.artifact_describer import ArtifactInfoJSONEncoder

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

    def __init__(self, os_distro_name):
        self.os_distro_name = os_distro_name

    def describe(self, artifact_names=[]):
        installed_artifacts = InstalledArtifacts([
            self.describe_installed_os(), 
            self.describe_installed_app('productid-app-helloworld')
        ])
        return json.dumps(installed_artifacts, indent=4, cls=ArtifactInfoJSONEncoder)

    def describe_installed_os(self):
        return InstalledArtifactInfo(
            self.os_distro_name, 
            ArtifactKind.OperatingSystem, 
            'f45e36b91cc08057b80de8de37443c3056dc0433c63c64ce849bc3e76749ea9a',
            '664fe8e40f178ccbdb2367e469eb19a9d2fbfe6683f3489e92b7d3aa5def5d44'
        )

    def describe_installed_app(self, name):
        return InstalledArtifactInfo(
            name, 
            ArtifactKind.Application, 
            'ed2bebe4a350f13d7a5e632cce3198b294b032754ad3cd6923bc7b0d4488144e'
        )