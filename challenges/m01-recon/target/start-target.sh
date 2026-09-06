#!/bin/sh
set -eu

key_directory=/tmp/offsec-ssh
mkdir -p "$key_directory"
chmod 700 "$key_directory"

if [ ! -f "$key_directory/ssh_host_ed25519_key" ]; then
    ssh-keygen -q -t ed25519 -N "" -f "$key_directory/ssh_host_ed25519_key"
fi

nginx
exec /usr/sbin/sshd -D -e -f /etc/ssh/sshd_config
