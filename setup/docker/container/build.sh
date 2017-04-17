#!/bin/sh
set -eu

cwd=$(dirname $0)
fyc_home=$(cd ${cwd}/../../.. && pwd)

usage() {
  echo "Usage: ${0##*/} [base|opencv|robot|webapp]"
}

if [ $# -lt 1 ]; then
  usage
  exit 1
fi

case "$1" in
  base | opencv | robot | webapp)
    repos="brainpad/fyc-$1"
    tag=$(date '+%Y%m%d%H%M')

    echo "${repos}:${tag}"
    echo ""

    docker build -t ${repos}:${tag} -f ${cwd}/${1}/Dockerfile ${fyc_home}
    docker tag ${repos}:${tag} ${repos}:latest
    ;;
  *)
    usage
    ;;
esac
