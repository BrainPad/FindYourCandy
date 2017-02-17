# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import importlib


def load_class(name):
    parts = name.split('.')
    module = importlib.import_module('.'.join(parts[:-1]))
    return getattr(module, parts[-1])
