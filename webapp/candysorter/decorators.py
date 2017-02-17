# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import g


def after_this_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f
