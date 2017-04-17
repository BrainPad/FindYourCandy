#!/bin/sh
set -eu

if [ $# -lt 2 ]; then
  echo "Usage: `basename $0` [host_file] [private_key_file]"
  exit 1
fi

cwd=$(dirname $0)

ansible-playbook \
  -u root \
  -i $1 \
  --private-key $2 \
  ${cwd}/site.yml
