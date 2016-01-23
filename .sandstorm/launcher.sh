#!/bin/bash
set -euo pipefail
# something something folders
mkdir -p /var/lib/mysql
mkdir -p /var/lib/nginx
mkdir -p /var/log
mkdir -p /var/log/mysql
mkdir -p /var/log/nginx
# Wipe /var/run, since pidfiles and socket files from previous launches should go away
# TODO someday: I'd prefer a tmpfs for these.
rm -rf /var/run
mkdir -p /var/run
mkdir -p /var/run/mysqld

UWSGI_SOCKET_FILE=/var/run/uwsgi.sock

# Ensure mysql tables created
HOME=/etc/mysql /usr/bin/mysql_install_db --force

# Spawn mysqld
HOME=/etc/mysql /usr/sbin/mysqld &

MYSQL_SOCKET_FILE=/var/run/mysqld/mysqld.sock
# Wait for mysql to bind its socket
while [ ! -e $MYSQL_SOCKET_FILE ] ; do
    echo "waiting for mysql to be available at $MYSQL_SOCKET_FILE"
    sleep .2
done

# Spawn uwsgi
HOME=/var uwsgi \
        --socket $UWSGI_SOCKET_FILE \
        --plugin python \
        --virtualenv /opt/app/env \
        --wsgi-file /opt/app/main.py &

# Wait for uwsgi to bind its socket
while [ ! -e $UWSGI_SOCKET_FILE ] ; do
    echo "waiting for uwsgi to be available at $UWSGI_SOCKET_FILE"
    sleep .2
done

# Start nginx.
/usr/sbin/nginx -g "daemon off;"

