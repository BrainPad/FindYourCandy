#!/bin/sh

sudo chmod 777 /dev/video0
sudo mkdir -p -m 777 /var/run/uwsgi
sudo chown brainpad:brainpad /var/run/uwsgi
sudo mkdir -p -m 777 /var/log/uwsgi
sudo chown brainpad:brainpad /var/log/uwsgi

sudo systemctl start uwsgi-webapp.service
