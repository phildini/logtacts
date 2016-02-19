#!/bin/bash
set -euo pipefail
VENV=/opt/app/env
if [ ! -d $VENV ] ; then
    virtualenv $VENV
else
    echo "$VENV exists, moving on"
fi

if [ -f /opt/django-sandstorm/setup.py ] ; then
    pushd /opt/django-sandstorm/
    $VENV/bin/pip uninstall django-sandstorm
    $VENV/bin/pip install -e .
    popd
else
    rm -f $VENV/lib/python2.7/site-packages/django-sandstorm.egg-link
fi

if [ -f /opt/app/requirements.txt ] ; then
    $VENV/bin/pip install -r /opt/app/requirements.txt
fi
