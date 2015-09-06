#! /bin/bash
source /home/deploy/.bashrc
cd /home/deploy/Env/logtacts
source bin/activate
cd /home/deploy/logtacts
python manage.py send_invites --settings=logtacts.prod_settings
deactivate