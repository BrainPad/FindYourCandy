#!/bin/sh

cwd=$(dirname $0)
cd $cwd

./stop_uwsgi_robot.sh
./start_uwsgi_robot.sh
