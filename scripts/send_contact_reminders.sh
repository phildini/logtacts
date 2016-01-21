#! /bin/bash
source /home/deploy/.bashrc
cd /home/deploy/Env/logtacts
source bin/activate
cd /home/deploy/logtacts
python manage.py send_contact_reminders --settings=logtacts.prod_settings
deactivate