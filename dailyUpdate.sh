#!/usr/bin/env bash

basePath="."
if [[ ! -z $1 ]]; then
  basePath=$(dirname $0)
fi

cd ${basePath}
echo $0
echo "Pwd"
pwd

source ./env/bin/activate

python -u ./scrpyTPB.py --pages=30