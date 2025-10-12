#!/bin/sh
set -e

if [ -z "$SERVICE_TYPE" ]; then
    echo "Please set SERVICE_TYPE to either 'fastapi' or 'fastmcp'"
    exit 1
fi

exec /usr/bin/supervisord -c /etc/supervisord.conf
