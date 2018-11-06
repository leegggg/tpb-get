#!/usr/bin/env bash

basePath="."
if [[ ! -z $1 ]]; then
  basePath=$1
fi

echo basePath

cd ${basePath}

source ./env/bin/activate

cd app
python -u ./scrpyTPB.py --pages=30