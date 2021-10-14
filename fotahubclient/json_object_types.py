from enum import Enum

from fotahubclient.json_encode_decode import PascalCasedObjectArrayJSONDecoder

UPDATE_DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class ArtifactKind(Enum):
    OperatingSystem = 1
    Application = 2

class UpdateStatus(Enum):
    downloaded = 1
    activated = 2
    confirmed = 3 
    reverted = 4
    failed = 5

class InstalledArtifactInfo(object):
    def __init__(self, name, kind, installed_revision, rollback_revision=None):
        self.name = name
        self.kind = kind
        self.installed_revision = installed_revision
        self.rollback_revision = rollback_revision

class InstalledArtifacts(object):
    def __init__(self, installed_artifacts=[]):
        self.installed_artifacts = installed_artifacts

class UpdateStatusInfo(object):
    def __init__(self, artifact_name, artifact_kind, revision, install_date, status, error_message=None):
        self.artifact_name = artifact_name
        self.artifact_kind = artifact_kind
        self.revision = revision
        self.install_date = install_date
        self.status = status
        self.error_message = error_message

class UpdateStatuses(object):
    def __init__(self, update_statuses=[]):
        self.update_statuses = update_statuses

class UpdateStatusesJSONDecoder(PascalCasedObjectArrayJSONDecoder):
    def __init__(self,):
        super().__init__(UpdateStatuses, UpdateStatusInfo, [ArtifactKind, UpdateStatus])