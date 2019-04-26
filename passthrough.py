#!/usr/bin/python3

#  Copyright 2019 Linaro Limited
#  Author: Dave Pigott <dave.pigott@linaro.org>

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  USB device passthrough for docker containers

import pyudev
import argparse
import os
import docker


def get_device_numbers(serial_no):
    result = None, None
    context = pyudev.Context()

    devices = context.list_devices(subsystem='usb')

    for device in devices:
        serial = device.attributes.get("serial")
        if serial is not None and serial_no in serial.decode("utf-8"):
            result = os.major(device.device_number), os.minor(device.device_number)
            break

    return result


def pass_device_into_container(instance, major, minor):
    client = docker.from_env()

    container = client.containers.get(instance)

    allow_devices = open("/sys/fs/cgroup/devices/docker/%s/devices.allow" % container.id, "w")
    allow_devices.write("c %s:%s rwm" % (major, minor))
    allow_devices.close()


def main():
    parser = argparse.ArgumentParser(description='USB device passthrough for docker containers', add_help=False)

    parser.add_argument("-d", "--device_serial", type=str, required=True,
                        help="Devices serial number")
    parser.add_argument("-i", "--instance", type=str, required=True,
                        help="Docker instance")

    options = parser.parse_args()

    major, minor = get_device_numbers(options.device_serial)

    if major is not None:
        pass_device_into_container(options.instance, major, minor)


if __name__ == '__main__':
    main()
