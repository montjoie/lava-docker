#!/bin/bash

postgres-ready () {
  echo "Waiting for lavaserver database to be active"
  while (( $(ps -ef | grep -v grep | grep postgres | grep lavaserver | wc -l) == 0 ))
  do
    echo -n "."
    sleep 1
  done
  echo 
  echo "[ ok ] LAVA server ready"
}

start () {
  echo "Starting $1"
  if (( $(ps -ef | grep -v grep | grep -v add_device | grep -v dispatcher-config | grep "$1" | wc -l) > 0 ))
  then
    echo "$1 appears to be running"
  else
    service "$1" start
  fi
}

#remove lava-pid files incase the image is stored without first stopping the services
rm -f /var/run/lava-*.pid 2> /dev/null

/etc/init.d/postgresql start

# always reset the lavaserver user, since its password could have been reseted in a "docker build --nocache"
if [ ! -e /root/pg_lava_password ];then
	< /dev/urandom tr -dc A-Za-z0-9 | head -c16 > /root/pg_lava_password
fi
sudo -u postgres psql -c "ALTER USER lavaserver WITH PASSWORD '$(cat /root/pg_lava_password)';" || exit $?
sed -i "s,^LAVA_DB_PASSWORD=.*,LAVA_DB_PASSWORD='$(cat /root/pg_lava_password)'," /etc/lava-server/instance.conf || exit $?

/setup.sh || exit $?

start apache2 || exit $?
start lava-logs || exit $?
start lava-master || exit $?
start lava-coordinator || exit $?
start lava-slave || exit $?
start lava-server-gunicorn || exit $?
start tftpd-hpa || exit $?

postgres-ready
service apache2 reload #added after the website not running a few times on boot
