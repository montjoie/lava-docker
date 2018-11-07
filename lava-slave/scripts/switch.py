#!/usr/bin/env python3

import brainstem
from brainstem.result import Result
import time
import sys

ret = 0

if len(sys.argv) > 1:
    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        sys.exit(1)


# help(stem.usb)
# help(brainstem.stem)

ch = 2
stem = brainstem.stem.USBHub3p()
result = stem.discoverAndConnect(brainstem.link.Spec.USB)
#Check error
if result == (Result.NO_ERROR):
    result = stem.system.getSerialNumber()
    print ("Connected to USBStem with serial number: 0x%08X" % result.value)

    if sys.argv[1] == "reset":
        stem.usb.setPortDisable(sys.argv[2])
        time.sleep(1)
        stem.usb.setPortEnable(sys.argv[2])
    elif sys.argv[1] == "power_on":
        stem.usb.setPortEnable(sys.argv[2])
    elif sys.argv[1] == "power_off":
        stem.usb.setPortDisable(sys.argv[2])
    else:
        print("ERROR: unknown keyword %s" % sys.argv[1])
        ret = 1
    #stem.usb.setPortDisable(ch)
    #stem.usb.setPortEnable(ch)
    #stem.usb.setPowerEnable(ch)     #for independent power control
    #stem.usb.setDataEnable(ch)      #for independent data control

    #while True:
    #    resulta = stem.usb.getPortCurrent(ch)
    #    resultv = stem.usb.getPortVoltage(ch)
    #    print "voltage= " + str(resultv.value) + "\t" + "current=" + str(resulta.value)
    #    time.sleep(0.1)
else:
    print ('Could not find a module.\n')
    ret = 1

stem.disconnect()
sys.exit(ret)
