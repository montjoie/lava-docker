#!/bin/sh

# TODO remove hardcoded 10.201.2.5 / 6
find /root/devices |grep -q hsdk
if [ $? -eq 0 ];then
       /usr/local/bin/hsdk.py --name /dev/hsdk-01 --netport 64000 --resetcmd "/usr/local/bin/acme-cli -s 10.201.2.5 reset 6" &
fi

find /root/devices |grep -q hifive
if [ $? -eq 0 ];then
       /usr/local/bin/hsdk.py --name /dev/hifive-unleashed-a00-01 --netport 64001 &
fi

