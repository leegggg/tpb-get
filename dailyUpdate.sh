#!/usr/bin/env bash

basePath=$(dirname $0)
if [[ ! -z $1 ]]; then
  basePath=$1
fi

cd ${basePath}
echo "Pwd: $(pwd)"

source ./env/bin/activate

python -u ./scrpyTPB.py --pages=30 --jobs=./bigCata.txt