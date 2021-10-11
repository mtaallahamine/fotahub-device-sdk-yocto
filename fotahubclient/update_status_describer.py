from enum import Enum
import json
from datetime import datetime

from fotahubclient.base_describer import ArtifactKind
from fotahubclient.base_describer import PascalCaseJSONEncoder

class UpdateStatus(Enum):
    downloaded = 1
    activated = 2
    confirmed = 3 
    reverted = 4
    failed = 5

class UpdateInfo(object):

    def __init__(self, artifact_name, artifact_kind, revision, install_date, status, error_message=None):
        self.artifact_name = artifact_name
        self.artifact_kind = artifact_kind
        self.revision = revision
        self.install_date = install_date
        self.status = status
        self.error_message = error_message

class UpdateStatuses(object):

    def __init__(self, update_statuses):
        self.update_statuses = update_statuses

class UpdateStatusDescriber(object):

    def __init__(self, config):
        self.config = config

    def describe(self, artifact_names=[]):
        update_statuses = UpdateStatuses([
            self.describe_os_update_status(), 
            self.describe_app_update_status('productid-app-helloworld')
        ])
        return json.dumps(update_statuses, indent=4, cls=PascalCaseJSONEncoder)

    def describe_os_update_status(self):
        return UpdateInfo(
            self.config.os_distro_name, 
            ArtifactKind.OperatingSystem, 
            'f45e36b91cc08057b80de8de37443c3056dc0433c63c64ce849bc3e76749ea9a',
            datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            UpdateStatus.confirmed
        )

    def describe_app_update_status(self, name):
        return UpdateInfo(
            name, 
            ArtifactKind.Application, 
            '9a4d5186320d06bc5a543f99c9fe631995d6182b151f40d829bfce795e6a2cac',
            datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            UpdateStatus.failed,
            "Failed to start 'helloworld' application (exit code: 1)"
        )