#!/bin/bash
cd /home/deploy/Env/logtacts/
source bin/activate
cd /home/deploy/logtacts/
git pull --rebase
pip install -r requirements.txt
kill -HUP `cat /tmp/logtacts-master.pid`
