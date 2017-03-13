#!/bin/sh

cwd=$(dirname $0)
cd $cwd

./stop_nginx.sh
./stop_uwsgi_robot.sh
./stop_uwsgi_webapp.sh
