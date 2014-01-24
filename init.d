#!/bin/bash

### Maintain compatibility with chkconfig
# chkconfig: 12345 15 99
# description: lvm-init

### BEGIN INIT INFO
# Provides:          lvm-init
# Required-Start:    $local_fs
# Required-Stop:     $local_fs
# Default-Start:     1 2 3 4 5
# Default-Stop:      0 6
# Short-Description: lvm-init
# Description:       lvm-init
### END INIT INFO

PATH=/sbin:/bin:/usr/sbin:/usr/bin

case "$1" in
  start)
    /sbin/lvm-init
    ;;
  *)
    echo "action not supported"
    ;;
esac
exit 0
