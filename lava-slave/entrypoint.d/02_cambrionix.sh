#!/bin/sh

# cambrionix potato2
if [ -e /dev/cambrionix-01 ];then
	/usr/local/bin/pycambrionyx.py --daemon --name /dev/cambrionix-01 &
fi
# cambrionix LABtest
if [ -e /dev/cambrionix-02 ];then
	/usr/local/bin/pycambrionyx.py --daemon --name /dev/cambrionix-02 &
fi
# cambrionix potato3
if [ -e /dev/cambrionix-03 ];then
	/usr/local/bin/pycambrionyx.py --daemon --name /dev/cambrionix-03 &
fi
# cambrionix kvim3
if [ -e /dev/cambrionix-04 ];then
	/usr/local/bin/pycambrionyx.py --daemon --name /dev/cambrionix-04 --starts 8 --startoff 1,2,3,4,5,6,7 &
fi
# cambrionix LABtest
if [ -e /dev/cambrionix16-01 ];then
	/usr/local/bin/pycambrionyx.py --daemon --name /dev/cambrionix16-01 --starts 1,2,3,4,5,6,7,8 --startoff 9,10,11,12,13,14,15,16 --netport 64002 &
fi
# cambrionix potato4
if [ -e /dev/cambrionix16-02 ];then
	/usr/local/bin/pycambrionyx.py --daemon --name /dev/cambrionix16-02 --startoff 1,2,3,4,5,6,7,8 --starts 9,10,11,12,13,14,15,16  &
fi
# cambrionix potato
if [ -e /dev/cambrionix16-03 ];then
	/usr/local/bin/pycambrionyx.py --daemon --name /dev/cambrionix16-03 --starts 1,2,3,4,5,6,7,8 --startoff 9,10,11,12,13,14,15,16  &
fi
