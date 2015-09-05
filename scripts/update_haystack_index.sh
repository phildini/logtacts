#! /bin/bash
source /home/deploy/.bashrc
cd /home/deploy/Env/logtacts
source bin/activate
cd /home/deploy/logtacts
python manage.py update_index --age=1 --settings=logtacts.prod_settings
deactivate