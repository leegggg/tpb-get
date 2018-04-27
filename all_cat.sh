#!/bin/bash
#virtualenv --python /usr/bin/python3 .politiqueJournalNpl
set -e

for cata in $(cat all_cat.txt)
do
    echo ${cata}
    python -u scrpyTPB.py --mirrordb=/home/ylin/tpbdb/tpbtorrent.db \
        --torrentdb=/home/ylin/tpbdb/tpbtorrent.db \
        --offset=0 --pages=36 \
        --log-level=2 \
        --path=${cata} &
done