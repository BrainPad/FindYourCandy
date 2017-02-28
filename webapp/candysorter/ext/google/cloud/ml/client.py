# Copyright 2017 BrainPad Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import, division, print_function, unicode_literals

from google.cloud.client import JSONClient
from google.cloud.iterator import HTTPIterator

from candysorter.ext.google.cloud.ml._http import Connection
from candysorter.ext.google.cloud.ml.job import Job


class Client(JSONClient):
    _connection_class = Connection

    def list_jobs(self, filter_=None, page_token=None, page_size=None):
        extra_params = {}
        if filter_ is not None:
            extra_params['filter'] = filter_
        if page_size is not None:
            extra_params['pageSize'] = page_size

        path = '/projects/{project}/jobs'.format(project=self.project)

        return HTTPIterator(
            client=self, path=path, item_to_value=_item_to_job, items_key='jobs',
            page_token=page_token, extra_params=extra_params)

    def get_job(self, name):
        job = Job(name, self)
        job.reload()
        return job


def _item_to_job(iterator, resource):
    return Job.from_api_repr(resource, iterator.client)
