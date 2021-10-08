from enum import Enum
import json
from json import JSONEncoder
import stringcase

def to_camelcased_dict(obj):
    return { stringcase.capitalcase(stringcase.camelcase(k)): v for k, v in obj.__dict__.items() }

class ArtifactKind(Enum):
    OperatingSystem = 1
    Application = 2

class UpdateStatus(Enum):
    downloaded = 1
    activated = 2
    confirmed = 3 
    reverted = 4
    failed = 5

class ArtifactInfo(object):
    def __init__(self, name, kind, current_revision, rollback_revision=None):
        self.name = name
        self.kind = kind
        self.current_revision = current_revision
        self.rollback_revision = rollback_revision

class UpdateInfo(object):
    def __init__(self, revision, status, error_message=None):
        self.revision = revision
        self.status = status
        self.error_message = error_message

class UpdateStatusInfo(object):
    def __init__(self, artifact_info, update_info):
        self.artifact_info = artifact_info
        self.update_info = update_info

class UpdateStatusInfoEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        else:
            return to_camelcased_dict(obj)

class UpdateStatusDescriber(object):

    def describe_os_update_status(self):
        return UpdateStatusInfo(
            ArtifactInfo(
                "productid-os-raspberrypi3", 
                ArtifactKind.OperatingSystem, 
                'f45e36b91cc08057b80de8de37443c3056dc0433c63c64ce849bc3e76749ea9a', 
                '664fe8e40f178ccbdb2367e469eb19a9d2fbfe6683f3489e92b7d3aa5def5d44'),
            UpdateInfo(
                'f45e36b91cc08057b80de8de37443c3056dc0433c63c64ce849bc3e76749ea9a',
                UpdateStatus.confirmed
            )
        )

    def describe_app_update_status(self, name):
        return UpdateStatusInfo(
            ArtifactInfo(
                name, 
                ArtifactKind.Application, 
                'ed2bebe4a350f13d7a5e632cce3198b294b032754ad3cd6923bc7b0d4488144e'),
            UpdateInfo(
                '9a4d5186320d06bc5a543f99c9fe631995d6182b151f40d829bfce795e6a2cac',
                UpdateStatus.failed,
                "Failed to start 'helloworld' application (exit code: 1)"
            )
        )

    def describe_update_statuses(self):
        update_statuses = [self.describe_os_update_status(), self.describe_app_update_status('productid-app-helloworld')]
        return json.dumps(update_statuses, indent=4, cls=UpdateStatusInfoEncoder)