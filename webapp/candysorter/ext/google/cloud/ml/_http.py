# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from google.cloud import _http


class Connection(_http.JSONConnection):
    API_BASE_URL = 'https://ml.googleapis.com'
    API_VERSION = 'v1beta1'
    API_URL_TEMPLATE = '{api_base_url}/{api_version}{path}'
    SCOPE = ('https://www.googleapis.com/auth/cloud-platform',)
