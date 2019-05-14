#!/usr/bin/env python3

import serial
import argparse
import time
import os
import socket
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--debug", "-d", type=bool, help="tty name")
parser.add_argument("--name", "-n", type=str, help="tty name")
parser.add_argument("--port", "-p", type=int, help="Cambrionix port to control")
parser.add_argument("--netport", type=int, help="Nerwork port", default=12346)
parser.add_argument("--resetcmd", type=str, help="reset")

args = parser.parse_args()

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = socket.gethostname()
print("DEBUG: listen on %d" % args.netport)
s.bind(("0.0.0.0", args.netport))
s.setblocking(0)
s.listen(5)
clients = []
opened = False
loopn = 0
discard = 0
got_output = False
serial_timeout = 0

while True:
    loopn = loopn + 1
    try:
        c, addr = s.accept()
        c.setblocking(0)
        if args.debug:
            print("DEBUG: connected from ")
        clients.append(c)
    except socket.error:
        if args.debug:
            print("DEBUG: no new client")
    if len(clients) == 0:
        time.sleep(1)
        continue
    if not opened:
        try:
            ser = serial.Serial(args.name, 115200, timeout=1)
            opened = True
            got_output = False
            serial_timeout = 10
        except FileNotFoundError:
            if args.debug:
                print("RETRY %d" % loopn)
            time.sleep(1)
            continue
        except serial.serialutil.SerialException:
            if args.debug:
                print("RETRY %d" % loopn)
            time.sleep(1)
            continue
    nn = 0
    for client in clients:
        try:
            buf = client.recv(1024)
            nn = nn +1
            if len(buf) == 0:
                if args.debug:
                    print("CLIENT DISCO")
                clients.remove(client)
            if len(buf) > 0:
                if args.debug:
                    print("DEBUG: client %d send %s data" % (nn, len(buf)))
                    print("ENDBUF")
                bubu = buf.decode("UTF-8").rstrip("\n")
                ser.write(bubu.encode("UTF-8"))
                discard = len(buf)
        except OSError as e:
            if args.debug:
                print("DEBUG: nothing for %s %d" % (client, e.errno))
    try:
        #b = ser.read(1024)
        if args.debug:
            print("DEBUG: serial recv")
        b = ser.readline()
        if (len(b) > 0):
            got_output = True
            if discard == len(b):
                discard = 0
                continue
            if args.debug:
                print("SERIAL %d" % len(b))
            nn = 0
            for client in clients:
                if args.debug:
                    print("Send to %d" % nn)
                nn = nn +1
                client.send(b)
        else:
            if not got_output and args.resetcmd:
                print("DEBUG: initial wait for output")
                time.sleep(1)
                serial_timeout = serial_timeout - 1
                if serial_timeout == 0:
                    print("RESET board !!!!!!")
                    subprocess.run(args.resetcmd, shell=True)
    except serial.serialutil.SerialException:
        ser.close()
        if args.debug:
            print("DISCO")
        opened = False


sys.exit(0)
