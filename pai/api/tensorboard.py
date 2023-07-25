import logging
from typing import Optional

from pai.api.base import PaginatedResult, PAIServiceName, WorkspaceScopedResourceAPI
from pai.libs.alibabacloud_pai_dlc20201203.models import (
    CreateTensorboardRequest,
    CreateTensorboardResponseBody,
    DeleteTensorboardRequest,
    GetTensorboardRequest,
    ListTensorboardsRequest,
    StartTensorboardRequest,
    StopTensorboardRequest,
    Tensorboard,
)

logger = logging.getLogger(__name__)


class TensorBoardAPI(WorkspaceScopedResourceAPI):

    BACKEND_SERVICE_NAME = PAIServiceName.PAI_DLC

    _get_method = "get_tensorboard_with_options"
    _list_method = "list_tensorboards_with_options"
    _create_method = "create_tensorboard_with_options"
    _delete_method = "delete_tensorboard_with_options"
    _start_method = "start_tensorboard_with_options"
    _stop_method = "stop_tensorboard_with_options"

    def get(self, tensorboard_id: str):
        request = GetTensorboardRequest()
        resp: Tensorboard = self._do_request(
            method_=self._get_method, tensorboard_id=tensorboard_id, request=request
        )
        return resp.to_map()

    def create(
        self,
        uri: str,
        display_name: str,
        source_id: Optional[str] = None,
        source_type: Optional[str] = None,
        summary_relative_path: Optional[str] = None,
        data_source_type: Optional[str] = None,
        dataset_id: Optional[str] = None,
        max_running_time_minutes: Optional[int] = None,
        **kwargs,
    ):
        request = CreateTensorboardRequest(
            data_source_type=data_source_type,
            uri=uri,
            display_name=display_name,
            summary_relative_path=summary_relative_path,
            source_id=source_id,
            source_type=source_type,
            data_source_id=dataset_id,
            max_running_time_minutes=max_running_time_minutes,
            **kwargs,
        )
        resp: CreateTensorboardResponseBody = self._do_request(
            method_=self._create_method, request=request
        )
        return resp.tensorboard_id

    def delete(self, tensorboard_id: str):
        request = DeleteTensorboardRequest()
        self._do_request(
            self._delete_method, tensorboard_id=tensorboard_id, request=request
        )

    def start(self, tensorboard_id: str):
        request = StartTensorboardRequest()

        self._do_request(
            self._start_method,
            tensorboard_id=tensorboard_id,
            request=request,
        )

    def list(
        self,
        source_type: Optional[str] = None,
        source_id: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 50,
        **kwargs,
    ) -> PaginatedResult:
        request = ListTensorboardsRequest(
            page_size=page_size,
            page_number=page_number,
            source_id=source_id,
            source_type=source_type,
            **kwargs,
        )
        resp = self._do_request(
            self._list_method,
            request=request,
        )
        return self.make_paginated_result(resp)

    def stop(self):
        request = StopTensorboardRequest()
        self._do_request(
            self._stop_method,
            request=request,
        )
