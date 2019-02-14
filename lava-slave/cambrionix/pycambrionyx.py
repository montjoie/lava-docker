#!/usr/bin/env python

import serial
import argparse
import sys
import time
import os

def disable_port(port):
    print("Disable port %s" % port)
    ser.write(b"mode o %s\r\n" % port)
    time.sleep(0.200)
    x = ser.read(1024)
    timeout = 0
    if args.debug:
        print("=========")
        ser.write(b"state\r\n")
        x = ser.read(1024)
        print(x)
    while timeout < 10:
        ser.write(b"state %s\r\n" % port)
        x = ser.read(1024)
        if args.debug:
            print("==============")
        res = x.split(" ")
        if res[0] != 'state':
            print("Unexpected")
            print(res)
            return 1
        if res[4] != 'R':
            print("Unexpected")
            print(res)
            return 1
        if args.debug:
            print(res)
        if res[6] == 'O,':
            break
        time.sleep(0.5)
        timeout = timeout + 1
        print("Wait for port disabled %d/10" % timeout)
    return 0

def enable_port(port):
    print("Enable port %s" % args.port)
    ser.write(b"mode c %s 2\r\n" % args.port)
    time.sleep(0.250)
    x = ser.read(1024)
    timeout = 0
    while timeout < 10:
        ser.write(b"state %s\r\n" % port)
        x = ser.read(1024)
        if args.debug:
            print("==============")
        res = x.split(" ")
        if res[0] != 'state':
            print("Unexpected")
            print(res)
            return 1
        if res[4] != 'R':
            print("Unexpected")
            print(res)
            return 1
        if args.debug:
            print(res)
        # port charging
        if res[6] == 'C,':
            break
        # port profiling
        if res[6] == 'P,':
            break
        time.sleep(0.5)
        timeout = timeout + 1
        print("Wait for port enabled %d/10" % timeout)
    return 0

parser = argparse.ArgumentParser()
parser.add_argument("--name", "-n", type=str, help="tty name")
parser.add_argument("--port", "-p", type=str, help="tty name")
parser.add_argument("--timeout", "-t", type=int, help="timeout")
parser.add_argument("--off", action="store_true", help="turn off port")
parser.add_argument("--on", action="store_true", help="turn on prot")
parser.add_argument("--reset", action="store_true", help="reset port")
parser.add_argument("--debug", "-d", help="increase debug level", action="store_true")

args = parser.parse_args()

timeoutmax=60
if args.timeout:
    timeoutmax = args.timeout
lockdir="/tmp/cambrionix.lock"
ret = 1
while ret != 0:
    timeout = 0
    while os.path.exists(lockdir):
        print("DEBUG: wait for lock %d/%d" % (timeout, timeoutmax))
        time.sleep(1)
        timeout = timeout + 1
        if timeout > timeoutmax:
            print("ERROR: fail to lock")
            sys.exit(1)
    try:
        os.mkdir(lockdir)
        ret = 0
    except OSError:
        print("ERROR: mkdir")

ser = serial.Serial(args.name, 115200, timeout=1)

if args.off:
    disable_port(args.port)
if args.on:
    enable_port(args.port)
if args.reset:
    disable_port(args.port)
    enable_port(args.port)
#if args.state:
#    print_state()

ser.close()
os.rmdir(lockdir)
sys.exit(0)

print("=========")
ser.write(b"state\r\n")
x = ser.read(1024)
print(x)
ser.write(b"health\r\n")
x = ser.read(1024)
print(x)
ser.write(b"id\r\n")
x = ser.read(4096)
print(x)
ser.close()

# doc

# state
#portnum, mA, R?, [DA]?, [RIPCO], profile 4, uptime, watt

#A=arm
#D=disarm

#O = off
#I = idel
#P = profiling
#C = charging
