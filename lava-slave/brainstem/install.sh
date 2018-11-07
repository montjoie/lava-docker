#!/bin/sh

case $(uname -m) in
aarch64)
dpkg --add-architecture armhf || exit $?
apt-get update || exit $?
apt-get -y install python:armhf || exit $?
pip install /brainstem/arm32/brainstem-2.6.5-py2.py3-none-any.whl || exit $?
;;
*)
	echo "Unsupported arch"
;;
esac
