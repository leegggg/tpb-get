#!/bin/bash
#virtualenv --python /usr/bin/python3 .politiqueJournalNpl
home=~/
source ${home}politiqueJournalNpl/.politiqueJournalNpl/bin/activate
python ${home}politiqueJournalNpl/scrpyXinHuaShe.py --path=${home}xinhuanet/
deactivate
