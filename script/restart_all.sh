#!/bin/sh

cwd=$(dirname $0)
cd $cwd

./stop_all.sh
./start_all.sh
