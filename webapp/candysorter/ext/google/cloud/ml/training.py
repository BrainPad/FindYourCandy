# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals


class ScaleTier(object):
    BASIC = 'BASIC'
    STANDARD_1 = 'STANDARD_1'
    PREMIUM_1 = 'PREMIUM_1'
    BASIC_GPU = 'BASIC_GPU'
    CUSTOM = 'CUSTOM'


class TrainingInput(object):
    def __init__(self, package_uris, python_module, scale_tier=ScaleTier.BASIC,
                 region='us-central1'):
        self.package_uris = package_uris
        self.python_module = python_module
        self.scale_tier = scale_tier
        self.region = region
        self._properties = {}

    @classmethod
    def from_api_repr(cls, resource):
        training_input = cls(package_uris=resource.get('packageUris'),
                             python_module=resource.get('pythonModule'),
                             scale_tier=resource.get('scaleTier'),
                             region=resource.get('region'))
        if 'args' in resource:
            training_input._properties['args'] = resource['args']
        return training_input

    def to_api_repr(self):
        resource = {
            'scaleTier': self.scale_tier,
            'packageUris': self.package_uris,
            'pythonModule': self.python_module,
            'region': self.region,
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
