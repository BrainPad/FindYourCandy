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

from flask import g
from werkzeug.contrib.cache import SimpleCache


class Cache(object):

    def __init__(self):
        self.cache = SimpleCache(default_timeout=1800)

    def get(self, key):
        return self.cache.get(self._key(key))

    def set(self, key, value):
        return self.cache.set(self._key(key), value)

    def delete(self, key):
        return self.cache.delte(self._key(key))

    def _key(self, key):
        return '{}:{}'.format(g.id, key)
