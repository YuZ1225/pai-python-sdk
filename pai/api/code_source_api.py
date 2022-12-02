from datetime import datetime
from typing import Any, Dict

from pai.api.base import PaginatedResult, WorkspaceScopedResourceAPI
from pai.common.consts import DEFAULT_PAGE_NUMBER, DEFAULT_PAGE_SIZE, PAIServiceName
from pai.libs.alibabacloud_aiworkspace20210204.client import Client
from pai.libs.alibabacloud_aiworkspace20210204.models import (
    CreateCodeSourceRequest,
    ListCodeSourcesRequest,
)


class CodeSourceAPI(WorkspaceScopedResourceAPI):
    """Class which provide API to operate CodeSource resource."""

    BACKEND_SERVICE_NAME = PAIServiceName.AIWORKSPACE

    _list_method = "list_code_sources_with_options"
    _get_method = "get_code_source_with_options"
    _delete_method = "delete_code_source_with_options"
    _create_method = "create_code_source_with_options"

    def __init__(self, workspace_id: str, acs_client: Client) -> None:
        super(CodeSourceAPI, self).__init__(
            workspace_id=workspace_id, acs_client=acs_client
        )

    @classmethod
    def _generate_display_name(cls, job):
        return "{}-{}".format(
            type(job).__name__, datetime.now().isoformat(sep="-", timespec="seconds")
        )

    def list(
        self,
        display_name=None,
        order=None,
        page_number=DEFAULT_PAGE_NUMBER,
        page_size=DEFAULT_PAGE_SIZE,
        sort_by=None,
    ) -> PaginatedResult:
        """Returns a List of CodeSource match the conditions.

        Args:
            display_name: Display name of the CodeSource.
            sort_by: Filed using in code source sort.
            order:
            page_size: Page size.
            page_number: Page number.

        Returns:
            list: A list of code source.

        """

        request = ListCodeSourcesRequest(
            display_name=display_name,
            order=order,
            page_number=page_number,
            page_size=page_size,
            sort_by=sort_by,
        )

        resp = self._do_request(method_=self._list_method, request=request).to_map()
        return self.make_paginated_result(resp)

    def count(
        self,
        display_name=None,
    ):
        """Returns count of CodeSource match the conditions.

        Args:
            display_name: Display name of the CodeSource.

        Returns:
            int: Count of code source.

        """

        request = ListCodeSourcesRequest(
            display_name=display_name,
        )
        result = self._do_request(self._list_method, request=request)
        return result.total_count

    def get_api_object_by_resource_id(self, resource_id):
        result = self._do_request(self._get_method, code_source_id=resource_id)
        return result.to_map()

    def get(self, id: str) -> Dict[str, Any]:
        """Get CodeSource by Id.

        Returns:
            Dict[str, Any]
        """
        return self.get_api_object_by_resource_id(resource_id=id)

    def delete(self, id):
        """Delete the CodeSource."""
        self._do_request(self._delete_method, code_source_id=id)

    def create(self, code_source):
        """Create a CodeSource resource."""

        request = CreateCodeSourceRequest().from_map(code_source.to_api_object())

        resp = self._do_request(self._create_method, request=request)

        return resp.code_source_id
