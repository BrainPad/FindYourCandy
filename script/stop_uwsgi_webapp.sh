#!/bin/sh

sudo systemctl stop uwsgi-webapp.service
pkill -f "/usr/local/bin/uwsgi --ini /etc/uwsgi/webapp.ini"
