#!/bin/sh
set -e

# Create directory for supervisord config files
mkdir -p /etc/supervisord.d

# Start supervisord with the new configuration path
/usr/bin/supervisord -c /etc/supervisord.d/supervisord.conf
