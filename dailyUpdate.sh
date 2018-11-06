#!/usr/bin/env bash

basePath="."
if [[ ! -z $1 ]]; then
  basePath=$(dirname $0)
fi

echo basePath

cd ${basePath}

source ./env/bin/activate

python -u ./scrpyTPB.py --pages=30