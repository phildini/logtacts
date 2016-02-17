#!/bin/bash
cd /home/deploy/Env/logtacts/
source bin/activate
cd /home/deploy/logtacts/
source .env
git pull --rebase
pip install -r requirements.txt
kill -HUP `cat /tmp/logtacts-master.pid`
curl https://intake.opbeat.com/api/v1/organizations/$OPBEAT_ORG_ID/apps/$OPBEAT_APP_ID/releases/ \
    -H "Authorization: Bearer $OPBEAT_SECRET_KEY" \
    -d rev=`git log -n 1 --pretty=format:%H` \
    -d branch=`git rev-parse --abbrev-ref HEAD` \
    -d status=completed
