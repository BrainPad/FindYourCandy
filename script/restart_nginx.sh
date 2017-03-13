#!/bin/sh

cwd=$(dirname $0)
cd $cwd

./stop_nginx.sh
./start_nginx.sh
