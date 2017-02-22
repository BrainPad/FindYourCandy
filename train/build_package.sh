#!/bin/sh

if [ $# -ne 1 ]; then
  echo "Usage: `basename $0` gcs_dir"
  exit 1
fi

rm -rf tmp output
mkdir tmp output

python setup.py \
  egg_info --egg-base tmp \
  build --build-base tmp --build-temp tmp \
  sdist --dist-dir output

gsutil cp output/trainer-0.0.0.tar.gz $1

rm -rf tmp output
