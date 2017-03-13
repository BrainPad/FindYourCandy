#!/bin/sh

cwd=$(dirname $0)
fyc_home=${cwd}/..

cd ${fyc_home}/setup/script
python robot_tune.py
