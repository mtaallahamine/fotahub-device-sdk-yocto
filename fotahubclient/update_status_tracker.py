import os
import logging
from datetime import datetime
from re import S

from fotahubclient.json_document_models import UPDATE_DATE_TIME_FORMAT, ArtifactKind
from fotahubclient.json_document_models import UpdateStatuses, UpdateStatusInfo, UpdateStatus

UPDATE_STATUS_INFO_MESSAGE_DEFAULTS = {
    UpdateStatus.reverted: 'Update reverted due to application-level or external request'
}

class UpdateStatusTracker(object):

    def __init__(self, config):
        self.logger = logging.getLogger()
        self.config = config
        self.update_statuses = UpdateStatuses()

    def __enter__(self):
        if os.path.isfile(self.config.update_status_path) and os.path.getsize(self.config.update_status_path) > 0:
            self.update_statuses = UpdateStatuses.load_update_statuses(self.config.update_status_path)
        return self 

    def record_os_update_status(self, status, revision=None, message=None, save_instantly=False):
        self.__record_update_status(self.config.os_distro_name, ArtifactKind.OperatingSystem, status, revision, message)
        if save_instantly:
            UpdateStatuses.save_update_statuses(self.update_statuses, self.config.update_status_path, True)

    def record_app_update_status(self, name, status, revision=None, message=None):
        self.__record_update_status(name, ArtifactKind.Application, status, revision, message)

    def record_fw_update_status(self, name, status, revision=None, message=None):
        self.__record_update_status(name, ArtifactKind.Firmware, status, revision, message)

    def __record_update_status(self, artifact_name, artifact_kind, status, revision=None, message=None):
        update_status_info = self.__lookup_update_status(artifact_name, artifact_kind)
        if update_status_info is not None:
            if update_status_info.status.is_final():
                update_status_info.revision = None
                update_status_info.install_date = datetime.today().strftime(UPDATE_DATE_TIME_FORMAT)
                update_status_info.message = None
            
            update_status_info.status = status
            if revision is not None:
                update_status_info.revision = revision
            if message is not None:
                update_status_info.message = message
        else:
            self.__append_update_status(
                UpdateStatusInfo(
                    artifact_name, 
                    artifact_kind, 
                    revision,
                    datetime.today().strftime(UPDATE_DATE_TIME_FORMAT),
                    status,
                    self.__ensure_default_message(status, message)
                )
            )

    def __ensure_default_message(self, status, message):
        if message is None and status in UPDATE_STATUS_INFO_MESSAGE_DEFAULTS.keys():
            return UPDATE_STATUS_INFO_MESSAGE_DEFAULTS[status]
        return message
        
    def __lookup_update_status(self, artifact_name, artifact_kind):
        for update_status_info in self.update_statuses.update_statuses:
            if update_status_info.artifact_name == artifact_name and update_status_info.artifact_kind == artifact_kind:
                return update_status_info
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