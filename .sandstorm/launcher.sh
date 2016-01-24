#!/bin/bash
set -euo pipefail
# something something folders
mkdir -p /var/lib/nginx
mkdir -p /var/log
mkdir -p /var/log/nginx
# Wipe /var/run, since pidfiles and socket files from previous launches should go away
# TODO someday: I'd prefer a tmpfs for these.
rm -rf /var/run
mkdir -p /var/run

UWSGI_SOCKET_FILE=/var/run/uwsgi.sock


/opt/app/env/bin/python /opt/app/manage.py migrate --settings=logtacts.sandstorm_settings

# Spawn uwsgi
HOME=/var uwsgi \
        --socket $UWSGI_SOCKET_FILE \
        --plugin python \
        --virtualenv /opt/app/env \
        --ini /opt/app/.sandstorm/service-config/logtacts-uwsgi.ini &

# Wait for uwsgi to bind its socket
while [ ! -e $UWSGI_SOCKET_FILE ] ; do
    echo "waiting for uwsgi to be available at $UWSGI_SOCKET_FILE"
    sleep .2
done

# Start nginx.
/usr/sbin/nginx -g "daemon off;"

