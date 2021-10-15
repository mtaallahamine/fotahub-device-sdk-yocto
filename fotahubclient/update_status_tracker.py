from enum import Enum
import json
import os
from datetime import datetime

from fotahubclient.json_document_models import UPDATE_DATE_TIME_FORMAT, ArtifactKind
from fotahubclient.json_document_models import UpdateStatuses, UpdateStatusInfo, UpdateStatus

UPDATE_STATUS_INFO_MESSAGE_DEFAULTS = {
    UpdateStatus.reverted: 'Update reverted due to application-level or external request'
}

class UpdateStatusTracker(object):

    def __init__(self, config):
        self.config = config
        self.update_statuses = UpdateStatuses()

    def __enter__(self):
        if os.path.isfile(self.config.update_status_path) and os.path.getsize(self.config.update_status_path) > 0:
            self.update_statuses = UpdateStatuses.load_update_statuses(self.config.update_status_path)
        return self 

    def record_os_update_status(self, status, revision=None, message=None):
        update_info = self.__lookup_os_update_status(self.config.os_distro_name)
        if update_info is not None:
            if revision is not None:
                update_info.revision = revision
            update_info.status = status
            if message is not None:
                update_info.message = message
        else:
            self.__append_update_status(
                UpdateStatusInfo(
                    self.config.os_distro_name, 
                    ArtifactKind.OperatingSystem, 
                    revision,
                    datetime.today().strftime(UPDATE_DATE_TIME_FORMAT),
                    status,
                    self.__ensure_default_message(status, message)
                )
        )

    def __ensure_default_message(self, status, message):
        if message is None:
            return UPDATE_STATUS_INFO_MESSAGE_DEFAULTS[status]
        return message
        
    def __lookup_os_update_status(self, os_distro_name):
        for update_status_info in self.update_statuses.update_statuses:
            print(update_status_info.artifact_kind)
            print(update_status_info.status)
            if update_status_info.artifact_name == os_distro_name and update_status_info.artifact_kind == ArtifactKind.OperatingSystem:
                return update_status_info
            else:
                return None

    def __lookup_app_update_status(self):
        return None

    def __append_update_status(self, update_status_info):
        self.update_statuses.update_statuses.append(update_status_info)

    def __exit__(self, exc_type, exc_val, exc_tb):
        UpdateStatuses.save_update_statuses(self.update_statuses, self.config.update_status_path)

class UpdateStatusDescriber(object):

    def __init__(self, config):
        self.config = config

    def describe_update_status(self, artifact_names=[]):
        if os.path.isfile(self.config.update_status_path) and os.path.getsize(self.config.update_status_path) > 0:
            return UpdateStatuses.dump_update_statuses(self.config.update_status_path)
        else:
            return UpdateStatuses().serialize()