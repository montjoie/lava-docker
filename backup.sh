#!/bin/sh

BACKUP_DIR="backup-$(date +%H%M_%d%m%Y)"

mkdir $BACKUP_DIR
cp boards.yaml $BACKUP_DIR

DOCKERID=$(docker ps |grep master | cut -d' ' -f1)
if [ -z "$DOCKERID" ];then
	exit 1
fi
docker exec -ti $DOCKERID sudo -u postgres pg_dump --create --clean lavaserver > $BACKUP_DIR/db_lavaserver || exit $?

docker exec -ti $DOCKERID tar czf /root/joboutput.tar.gz /var/lib/lava-server/default/media/job-output/ || exit $?
docker cp $DOCKERID:/root/joboutput.tar.gz $BACKUP_DIR/ || exit $?
