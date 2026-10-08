#!/bin/sh
# MySQL 容器入口：准备可被服务器读取的字符集配置，再交还官方启动流程。
# 任一步失败立即退出，未定义变量也报错，避免配置失败后仍继续启动。
set -eu

# Windows 绑定挂载呈现为全员可写，MySQL 会忽略它；复制到容器后收紧权限。
cp /config/mysql.cnf /etc/mysql/conf.d/charset.cnf
chmod 0644 /etc/mysql/conf.d/charset.cnf
# exec 保留官方入口的初始化逻辑，并让停止信号直接到达替换后的进程。
exec /usr/local/bin/docker-entrypoint.sh "$@"
