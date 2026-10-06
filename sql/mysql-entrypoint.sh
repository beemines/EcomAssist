#!/bin/sh
set -eu

# Windows 绑定挂载呈现为全员可写，MySQL 会忽略它；复制到容器后收紧权限。
cp /config/mysql.cnf /etc/mysql/conf.d/charset.cnf
chmod 0644 /etc/mysql/conf.d/charset.cnf
exec /usr/local/bin/docker-entrypoint.sh "$@"
