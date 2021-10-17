from enum import Enum
import json
import os

from fotahubclient.json_encode_decode import PascalCaseJSONEncoder, PascalCasedObjectArrayJSONDecoder

UPDATE_DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class ArtifactKind(Enum):
    OperatingSystem = 1
    Application = 2

class UpdateStatus(Enum):
    downloaded = 1
    verified = 2
    activated = 3
    confirmed = 4 
    reverted = 5
    failed = 6

    def is_final(self):
        return self == UpdateStatus.confirmed or self == UpdateStatus.reverted or self == UpdateStatus.failed

class InstalledArtifactInfo(object):
    def __init__(self, name, kind, installed_revision, rollback_revision=None):
        self.name = name
        self.kind = kind
        self.installed_revision = installed_revision
        self.rollback_revision = rollback_revision

class InstalledArtifacts(object):
    def __init__(self, installed_artifacts=[]):
        self.installed_artifacts = installed_artifacts

    def serialize(self):
        return json.dumps(self, indent=4, cls=PascalCaseJSONEncoder)

class UpdateStatusInfo(object):
    def __init__(self, artifact_name, artifact_kind, revision, install_date, status, message=None):
        self.artifact_name = artifact_name
        self.artifact_kind = artifact_kind
        self.revision = revision
        self.install_date = install_date
        self.status = status
        self.message = message

class UpdateStatuses(object):
    def __init__(self, update_statuses=[]):
        self.update_statuses = update_statuses

    def serialize(self):
        return json.dumps(self, indent=4, cls=PascalCaseJSONEncoder)

    @staticmethod
    def load_update_statuses(path):
        with open(path) as file:
            return json.load(file, cls=UpdateStatusesJSONDecoder)

    @staticmethod
    def save_update_statuses(update_statuses, path, flush_instantly=False):
        parent = os.path.dirname(path)
        if not os.path.isdir(parent):
            os.makedirs(parent, exist_ok=True)

        with open(path, 'w+', encoding='utf-8') as file:
            json.dump(update_statuses, file, ensure_ascii=False, indent=4, cls=PascalCaseJSONEncoder)
            
            if flush_instantly:
                # Flush the Python runtime's internal buffers
                file.flush()

                # Synchronize the operating system's buffers with file content on disk
                os.fsync(file.fileno())

    @staticmethod
    def dump_update_statuses(path):
        with open(path) as file: 
            return file.read()

class UpdateStatusesJSONDecoder(PascalCasedObjectArrayJSONDecoder):
    def __init__(self,):
        super().__init__(UpdateStatuses, UpdateStatusInfo, [ArtifactKind, UpdateStatus])