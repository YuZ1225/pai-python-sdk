# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from aliyunsdkcore.request import RoaRequest

class UpdatePipelineRequest(RoaRequest):

	def __init__(self):
		RoaRequest.__init__(self, 'PAIFlow', '2020-03-28', 'UpdatePipeline')
		self.set_uri_pattern('/api/core/v1.0/pipelines/[PipelineId]')
		self.set_method('PUT')

	def get_Manifest(self):
		return self.get_body_params().get('Manifest')

	def set_Manifest(self,Manifest):
		self.add_body_params('Manifest', Manifest)

	def get_PipelineId(self):
		return self.get_path_params().get('PipelineId')

	def set_PipelineId(self,PipelineId):
		self.add_path_param('PipelineId',PipelineId)