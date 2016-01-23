#!/bin/bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y nginx mysql-server libmysqlclient-dev uwsgi uwsgi-plugin-python build-essential python-dev python-virtualenv
# Set up nginx conf
unlink /etc/nginx/sites-enabled/default
cat > /etc/nginx/sites-available/sandstorm-python <<EOF
server {
    listen 8000 default_server;
    listen [::]:8000 default_server ipv6only=on;

    # Allow arbitrarily large bodies - Sandstorm can handle them, and requests
    # are authenticated already, so there's no reason for apps to add additional
    # limits by default.
    client_max_body_size 0;

    server_name localhost;
    root /opt/app;
    location /static/ {
        alias /opt/app/static/;
    }
    location / {
        uwsgi_pass unix:///var/run/uwsgi.sock;
        include uwsgi_params;
    }
}
EOF
ln -s /etc/nginx/sites-available/sandstorm-python /etc/nginx/sites-enabled/sandstorm-python
# patch mysql conf to not change uid
sed --in-place='' \
        --expression='s/^user\t\t= mysql/#user\t\t= mysql/' \
        /etc/mysql/my.cnf
# patch mysql conf to use smaller transaction logs to save disk space
cat <<EOF > /etc/mysql/conf.d/sandstorm.cnf
[mysqld]
# Set the transaction log file to the minimum allowed size to save disk space.
innodb_log_file_size = 1048576
# Set the main data file to grow by 1MB at a time, rather than 8MB at a time.
innodb_autoextend_increment = 1
EOF
# patch nginx conf to not bother trying to setuid, since we're not root
# also patch errors to go to stderr, and logs nowhere.
sed --in-place='' \
        --expression 's/^user www-data/#user www-data/' \
        --expression 's#^pid /run/nginx.pid#pid /var/run/nginx.pid#' \
        --expression 's/^\s*error_log.*/error_log stderr;/' \
        --expression 's/^\s*access_log.*/access_log off;/' \
        /etc/nginx/nginx.conf
service nginx stop
service mysql stop
systemctl disable nginx
systemctl disable mysql

