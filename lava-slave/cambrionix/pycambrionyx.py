#!/usr/bin/env python3

import serial
import argparse
import sys
import time
import os
import socket
import re

def disable_port(port):
    if args.debug:
        print("Disable port %d" % port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect(("127.0.0.1", int(args.netport)))
    sock.send(b"disable %d" % port)
    res = sock.recv(1024)
    print(res.decode("UTF8"))
    sock.close()
    return 0

def senable_port(port):
    if args.debug:
        print("SEnable port %d" % args.port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect(("127.0.0.1", int(args.netport)))
    sock.send(b"senable %d" % port)
    res = sock.recv(1024)
    print(res.decode("UTF8"))
    sock.close()
    return 0

def enable_port(port):
    if args.debug:
        print("Enable port %d" % args.port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect(("127.0.0.1", int(args.netport)))
    sock.send(b"enable %d" % port)
    res = sock.recv(1024)
    print(res.decode("UTF8"))
    sock.close()
    return 0

def cambrionix_daemon():
    ser = serial.Serial(args.name, 115200, timeout=1)
    ser.write(b"en_profile 1 0\r\n")
    ser.write(b"en_profile 2 1\r\n")
    ser.write(b"en_profile 3 0\r\n")
    ser.write(b"en_profile 4 0\r\n")
    ser.write(b"en_profile 5 0\r\n")
    if args.startc:
        for port in args.startc.split(","):
            print("DEBUG: Start port %d" % int(port))
            ser.write(b"mode c %d\r\n" % int(port))
    if args.starts:
        for port in args.starts.split(","):
            print("DEBUG: Start port %d" % int(port))
            ser.write(b"mode s %d\r\n" % int(port))
    if args.startoff:
        for port in args.startoff.split(","):
            print("DEBUG: Stop port %d" % int(port))
            ser.write(b"mode o %d\r\n" % int(port))
    if not args.startc and not args.startoff and not args.starts:
        print("DEBUG: old behaviour")
        for port in range(1,9):
            if os.path.exists("%s/port%d" % (args.statedir, port)):
                print("Keep port %d enabled" % port)
            else:
                ser.write(b"mode o %d\r\n" % port)
    x = ser.read(1024)
    if args.debug:
        print(x)

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host = socket.gethostname()
    s.bind(("0.0.0.0", int(args.netport)))
    s.setblocking(0)

    s.listen(5)

    clients = []
    cmds = {}
    ports = {}
    while True:
        if args.counterdir:
            ser.write(b"health\r\n")
            x = ser.read(1024)
            fcounter = open("%s/counters" % args.counterdir, "w")
            for hline in x.decode('UTF8').splitlines():
                print("CHECK: %s" % hline)
                if re.search("5V Now", hline):
                    v = re.sub("5V Now.* ", "", hline)
                    fcounter.write("5VNOW: %s\n" % v)
                if re.search("5V Min", hline):
                    v = re.sub("5V Min.* ", "", hline)
                    fcounter.write("5VMIN: %s\n" % v)
                if re.search("5V Max", hline):
                    v = re.sub("5V Max.* ", "", hline)
                    fcounter.write("5VMAX: %s\n" % v)
                if re.search("Temperature Now", hline):
                    v = re.sub(".* ", "", hline)
                    fcounter.write("TEMPNOW: %s\n" % v)
                if re.search("Temperature Max", hline):
                    v = re.sub(".* ", "", hline)
                    fcounter.write("TEMPMAX: %s\n" % v)
                if re.search("System up for", hline):
                    v = re.sub(".*for: *", "", hline)
                    fcounter.write("UPTIME: %s\n" % v)
            ser.write(b"logc 10\r\n")
            time.sleep(1.00)
            ser.write('\x03'.encode())
            x = ser.read(1024)
            for hline in x.decode('UTF8').splitlines():
                #print("CHECKma: %s" % hline)
                if re.search("^00", hline):
                    toks = hline.split(", ")
                    tokn = 0
                    for tok in toks:
                        if tokn >= 1 and tokn <= 8:
                            print("%d %s" % (tokn, tok))
                            fcounter.write("MA %d %s\n" % (tokn, tok.lstrip("0")))
                        tokn = tokn + 1
            fcounter.write("END\n")
            fcounter.close()

        ser.write(b"state\r\n")
        x = ser.read(1024)
        if args.debug:
            print(x)
            print(clients)
            print(cmds)
        try:
            c, addr = s.accept()
            c.setblocking(0)
            if args.debug:
                print('Got connection from', addr)
            clients.append(c)
        except socket.error:
            if args.debug:
                print("pas de nouveau client")
        nclient = len(clients)
        if nclient > 0:
            if args.debug:
                print("ya des clients: %d" % nclient)
            for client in clients:
                # check for already set cmds
                if client in cmds:
                    ser.write(b"state %s\r\n" % ports[client].encode())
                    x = ser.read(1024)
                    res = x.decode('UTF8').replace("  ", " ").split(" ")
                    if res[0] != 'state':
                        print("ERROR: Unexpected state")
                        print(res)
                        del cmds[client]
                        del ports[client]
                        client.send(b"FAIL: cannot find state\n")
                        client.close()
                        clients.remove(client)
                        continue
                    off = 4
                    if res[off] != 'R':
                        off = 3
                        if res[off] != 'R':
                            off = 5
                            if res[off] != 'R':
                                print("Unexpected R")
                                print(res)
                                del cmds[client]
                                del ports[client]
                                client.send(b"FAIL: cannot find state\n")
                                client.close()
                                clients.remove(client)
                                continue
                    # port charging
                    if res[off + 2] == 'C,' and cmds[client] == "enable":
                        fstate = open("%s/port%s" % (args.statedir, ports[client]), "w")
                        fstate.write("enabled")
                        fstate.close()
                        del cmds[client]
                        del ports[client]
                        client.send(b"Done\n")
                        client.close()
                        clients.remove(client)
                        continue
                    if res[off + 2] == 'S,' and cmds[client] == "senable":
                        fstate = open("%s/port%s" % (args.statedir, ports[client]), "w")
                        fstate.write("enabled")
                        fstate.close()
                        del cmds[client]
                        del ports[client]
                        client.send(b"Done\n")
                        client.close()
                        clients.remove(client)
                        continue
                    if res[off + 2] == 'O,' and cmds[client] == "disable":
                        if os.path.exists("%s/port%s" % (args.statedir, ports[client])):
                            os.remove("%s/port%s" % (args.statedir, ports[client]))
                        else:
                            print("WARN: disable without statefile")
                        del cmds[client]
                        del ports[client]
                        client.send(b"Done\n")
                        client.close()
                        clients.remove(client)
                        continue
                    if args.debug:
                        print("Wait more")
                    continue
                try:
                    buf = client.recv(1024)
                    print(buf)
                    bcmds = buf.decode('UTF-8').rstrip().split(" ")
                    if bcmds[0] == "quit":
                        client.close()
                        clients.remove(c)
                        #del cl["clients"][c]
                        continue
                    if bcmds[0] == "disable":
                        cmds[client] = bcmds[0]
                        ports[client] = bcmds[1]
                        ser.write(b"mode o %s\r\n" % bcmds[1].encode())
                        continue
                    if bcmds[0] == "enable":
                        cmds[client] = bcmds[0]
                        ports[client] = bcmds[1]
                        ser.write(b"mode c %s 2\r\n" % bcmds[1].encode())
                        continue
                    if bcmds[0] == "senable":
                        cmds[client] = bcmds[0]
                        ports[client] = bcmds[1]
                        ser.write(b"mode s %s 2\r\n" % bcmds[1].encode())
                        continue
                    if bcmds[0] == "health":
                        ser.write(b"health\r\n")
                        x = ser.read(1024)
                        if args.debug:
                            print(x)
                        client.send(x)
                        client.close()
                        clients.remove(client)
                        continue
                    client.send(b'Wrong command\n')
                    client.close()
                    clients.remove(client)
                except socket.error:
                    if args.debug:
                        print("Nothing new for")
        continue

    close(s)
    ser.close()
    sys.exit(0)

parser = argparse.ArgumentParser()
parser.add_argument("--name", "-n", type=str, help="tty name")
parser.add_argument("--port", "-p", type=int, help="Cambrionix port to control")
parser.add_argument("--timeout", "-t", type=int, help="timeout")
parser.add_argument("--off", action="store_true", help="turn off port")
parser.add_argument("--on", action="store_true", help="turn on prot")
parser.add_argument("--son", action="store_true", help="turn on prot")
parser.add_argument("--reset", action="store_true", help="reset port")
parser.add_argument("--sreset", action="store_true", help="reset port")
parser.add_argument("--debug", "-d", help="increase debug level", action="store_true")
parser.add_argument("--daemon", "-D", help="increase debug level", action="store_true")
parser.add_argument("--netport", help="Nerwork port", default=12346)
parser.add_argument("--counterdir", type=str, help="Where to store stats")
parser.add_argument("--statedir", type=str, help="Where to store port state", default="/var/cambrionix/")
parser.add_argument("--startc", type=str, help="Port list to enable(charge) at start (comma separated)")
parser.add_argument("--starts", type=str, help="Port list to enable(sync) at start (comma separated)")
parser.add_argument("--startoff", type=str, help="Port list to disable at start (comma separated)")

args = parser.parse_args()

if not os.path.exists(args.statedir):
    try:
        os.mkdir(args.statedir)
    except OSError as e:
        print(e)

timeoutmax=60
if args.timeout:
    timeoutmax = args.timeout

if args.daemon:
    cambrionix_daemon()

if args.off:
    disable_port(args.port)
if args.on:
    enable_port(args.port)
if args.son:
    senable_port(args.port)
if args.reset:
    disable_port(args.port)
    enable_port(args.port)
if args.sreset:
    disable_port(args.port)
    senable_port(args.port)

sys.exit(0)

# doc

# state
#portnum, mA, R?, [DA]?, [RIPCO], profile 4, uptime, watt

#A=arm
#D=disarm

#O = off
#I = idel
#P = profiling
#C = charging
