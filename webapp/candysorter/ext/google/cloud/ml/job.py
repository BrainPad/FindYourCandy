# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime

from pytz import UTC

from candysorter.ext.google.cloud.ml.training import TrainingInput


class Job(object):
    def __init__(self, name, client):
        self.name = name
        self._client = client
        self._properties = {}

    @classmethod
    def from_api_repr(cls, resource, client):
        name = resource.get('jobId')
        if name is None:
            raise KeyError('Resource lacks required identity information: ["jobId"]')
        job = cls(name=name, client=client)
        job._set_properties(resource)
        return job

    def to_api_repr(self):
        resource = {'jobId': self.name}
        training_input = self._properties.get('trainingInput')
        if training_input is not None:
            resource['trainingInput'] = training_input.to_api_repr()
        return resource

    def _set_properties(self, resource):
        self._properties.clear()
        cleaned = resource.copy()
        if 'createTime' in cleaned:
            cleaned['createTime'] = _rfc3339_to_datetime(cleaned['createTime'])
        if 'startTime' in cleaned:
            cleaned['startTime'] = _rfc3339_to_datetime(cleaned['startTime'])
        if 'endTime' in cleaned:
            cleaned['endTime'] = _rfc3339_to_datetime(cleaned['endTime'])
        if 'trainingInput' in cleaned:
            cleaned['trainingInput'] = TrainingInput.from_api_repr(resource['trainingInput'])
        self._properties.update(cleaned)

    @property
    def created(self):
        return self._properties.get('createTime')

    @property
    def started(self):
        return self._properties.get('startTime')

    @property
    def ended(self):
        return self._properties.get('endTime')

    @property
    def state(self):
        return self._properties.get('state')

    @property
    def error_message(self):
        return self._properties.get('errorMessage')

    @property
    def training_input(self):
        return self._properties.get('trainingInput')

    @training_input.setter
    def training_input(self, value):
        self._properties['trainingInput'] = value

    def _require_client(self, client):
        if client is None:
            client = self._client
        return client

    def reload(self, client=None):
        client = self._require_client(client)
        path = '/projects/{project}/jobs/{name}'.format(project=client.project, name=self.name)
        resp = client._connection.api_request(method='GET', path=path)
        self._set_properties(resource=resp)

    def create(self, client=None):
        client = self._require_client(client)
        path = '/projects/{project}/jobs'.format(project=client.project)
        client._connection.api_request(method='POST', path=path, data=self.to_api_repr())

    def cancel(self, client=None):
        client = self._require_client(client)
        path = '/projects/{project}/jobs/{name}:cancel'.format(
            project=client.project, name=self.name)
        client._connection.api_request(method='POST', path=path)


class State(object):
    STATE_UNSPECIFIED = 'STATE_UNSPECIFIED'
    QUEUED = 'QUEUED'
    PREPARING = 'PREPARING'
    RUNNING = 'RUNNING'
    SUCCEEDED = 'SUCCEEDED'
    FAILED = 'FAILED'
    CANCELLING = 'CANCELLING'
    CANCELLED = 'CANCELLED'


_RFC3339_SECONDS = '%Y-%m-%dT%H:%M:%SZ'


def _rfc3339_to_datetime(dt_str):
    return datetime.datetime.strptime(dt_str, _RFC3339_SECONDS).replace(tzinfo=UTC)
