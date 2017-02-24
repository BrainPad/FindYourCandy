# -*- coding: utf-8 -*-

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
