from enum import Enum
import json
import os
from datetime import datetime

from fotahubclient.json_object_types import UPDATE_DATE_TIME_FORMAT
from fotahubclient.json_object_types import ArtifactKind
from fotahubclient.json_object_types import UpdateStatuses
from fotahubclient.json_object_types import UpdateStatusInfo
from fotahubclient.json_object_types import UpdateStatus
from fotahubclient.json_encode_decode import PascalCaseJSONEncoder
from fotahubclient.json_object_types import UpdateStatusesJSONDecoder

class UpdateStatusTracker(object):

    def __init__(self, config):
        self.config = config
        self.update_statuses = UpdateStatuses()

    def __enter__(self):
        if os.path.isfile(self.config.update_status_path) and os.path.getsize(self.config.update_status_path) > 0:
            with open(self.config.update_status_path) as file:
                self.update_statuses = json.load(file, cls=UpdateStatusesJSONDecoder)
        return self 
        
    def record_os_update_status(self, status, revision=None, error_message=None):
        update_info = self.__lookup_os_update_status(self.config.os_distro_name)
        if update_info is not None:
            if revision is not None:
                update_info.revision = revision
            update_info.status = status
            if error_message is not None:
                update_info.error_message = error_message
        else:            
            self.__append_update_status(
                UpdateStatusInfo(
                    self.config.os_distro_name, 
                    ArtifactKind.OperatingSystem, 
                    revision,
                    datetime.today().strftime(UPDATE_DATE_TIME_FORMAT),
                    status,
                    error_message
                )
        )
        
    def __lookup_os_update_status(self, os_distro_name):
        for update_status_info in self.update_statuses.update_statuses:
            print(update_status_info.artifact_kind)
            print(update_status_info.status)
            if update_status_info.artifact_name == os_distro_name and update_status_info.artifact_kind == ArtifactKind.OperatingSystem:
                return update_status_info
            else:
                return None
    
    def __append_update_status(self, update_status_info):
        self.update_statuses.update_statuses.append(update_status_info)

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self.config.update_status_path, 'w', encoding='utf-8') as file:
            json.dump(self.update_statuses, file, ensure_ascii=False, indent=4, cls=PascalCaseJSONEncoder)

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
        return UpdateStatusInfo(
            self.config.os_distro_name, 
            ArtifactKind.OperatingSystem, 
            'f45e36b91cc08057b80de8de37443c3056dc0433c63c64ce849bc3e76749ea9a',
            datetime.today().strftime(UPDATE_DATE_TIME_FORMAT),
            UpdateStatus.confirmed
        )

    def describe_app_update_status(self, name):
        return UpdateStatusInfo(
            name, 
            ArtifactKind.Application, 
            '9a4d5186320d06bc5a543f99c9fe631995d6182b151f40d829bfce795e6a2cac',
            datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            UpdateStatus.failed,
            "Failed to start 'helloworld' application (exit code: 1)"
        )