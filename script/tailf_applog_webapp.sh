#!/bin/sh

cwd=$(dirname $0)
fyc_home=${cwd}/..

tail -f ${fyc_home}/webapp/logs/app.log
