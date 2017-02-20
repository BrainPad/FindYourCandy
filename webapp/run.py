# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse

from candysorter import create_app

parser = argparse.ArgumentParser(description='CandySorter WebApp')
parser.add_argument('--host', type=str, default='0.0.0.0')
parser.add_argument('--port', type=int, default=18000)
args = parser.parse_args()

app = create_app()

if __name__ == '__main__':
    app.run(host=args.host, port=args.port)
