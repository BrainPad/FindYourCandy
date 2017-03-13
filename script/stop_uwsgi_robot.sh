#!/bin/sh

sudo systemctl stop uwsgi-robot.service
pkill -f "/usr/local/bin/uwsgi --ini /etc/uwsgi/robot.ini"
