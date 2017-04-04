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


class ScaleTier(object):
    BASIC = 'BASIC'
    STANDARD_1 = 'STANDARD_1'
    PREMIUM_1 = 'PREMIUM_1'
    BASIC_GPU = 'BASIC_GPU'
    CUSTOM = 'CUSTOM'


class TrainingInput(object):
    def __init__(self, package_uris, python_module, scale_tier=ScaleTier.BASIC,
                 region='us-central1', runtime_version='1.0'):
        self.package_uris = package_uris
        self.python_module = python_module
        self.scale_tier = scale_tier
        self.region = region
        self.runtime_version = runtime_version
        self._properties = {}

    @classmethod
    def from_api_repr(cls, resource):
        training_input = cls(package_uris=resource.get('packageUris'),
                             python_module=resource.get('pythonModule'),
                             scale_tier=resource.get('scaleTier'),
                             region=resource.get('region'),
                             runtime_version=resource.get('runtimeVersion'))
        if 'args' in resource:
            training_input._properties['args'] = resource['args']
        return training_input

    def to_api_repr(self):
        resource = {
            'scaleTier': self.scale_tier,
            'packageUris': self.package_uris,
            'pythonModule': self.python_module,
            'region': self.region,
            'runtimeVersion': self.runtime_version,
        }
        _args = self._properties.get('args')
        if _args is not None:
            resource['args'] = _args
        return resource

    @property
    def args(self, value):
        return self._properties.get('args')

    @args.setter
    def args(self, value):
        self._properties['args'] = value

    def with_args(self, *args):
        _args = self._properties.setdefault('args', [])
        _args.extend(args)
