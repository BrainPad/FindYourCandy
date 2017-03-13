#!/bin/sh

cwd=$(dirname $0)
cd $cwd

./start_nginx.sh
./start_uwsgi_robot.sh
./start_uwsgi_webapp.sh
