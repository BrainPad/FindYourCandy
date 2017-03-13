#!/bin/sh

cwd=$(dirname $0)
cd $cwd

./stop_uwsgi_webapp.sh
./start_uwsgi_webapp.sh
