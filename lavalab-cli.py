#!/usr/bin/env python3

import xmlrpc.client
import sys
import os

# Doc on LAVA API https://validation.linaro.org/api/help/

noact = False

def usage():
    print("lavalab-cli [-n] action workername")
    print("lavalab-cli [-n] maintainance workername")
    print("lavalab-cli [-n] backfrommaintainance workername")

# Check if jobs ran on workername "$1"
# return 1 if yes
def check_jobs_on_worker(workername):
    server = xmlrpc.client.ServerProxy(os.environ.get("LAVAURI"))
    if workername == "all":
        workerlist = server.scheduler.workers.list()
        for worker in workerlist:
            if worker == 'lava-logs' or  worker == 'master':
                continue
            ret = check_jobs_on_worker(worker)
            if ret != 0:
                return ret
        return 0
    print("check_jobs_on_worker on %s" % workername)
    # get list of all devices runnning on workername
    devices_list = {}
    devlist = server.scheduler.devices.list()
    for device in devlist:
        devinfo = server.scheduler.devices.show(device["hostname"])
        if devinfo["worker"] == workername:
            print("\tDEBUG: Add %s to checklist" % device["hostname"])
#        else:
#            print("DEBUG: %s not on %s" % (device["hostname"], workername))
    print("DEBUG: get joblist")
    try:
        jlist = server.scheduler.jobs.list('RUNNING')
        for job in jlist:
            job_detail = server.scheduler.job_details(job["id"])
            if job_detail["actual_device_id"] in devices_list:
                return 1
    except xmlrpc.client.Fault as e:
        if e.faultCode == 404:
            return 0
        print(e)
        return 1
    return 0

def set_devices_unknown(workername):
    server = xmlrpc.client.ServerProxy(os.environ.get("LAVAURI"), allow_none=True)
    if workername == "all":
        workerlist = server.scheduler.workers.list()
        for worker in workerlist:
            if worker == 'lava-logs' or  worker == 'master':
                continue
            ret = set_devices_unknown(worker)
            if ret != 0:
                return ret
        return 0
    # get list of all devices runnning on workername
    print("INFO: Set all devices of %s to unknown" % workername)
    devlist = server.scheduler.devices.list()
    for device in devlist:
        devinfo = server.scheduler.devices.show(device["hostname"])
        if devinfo["worker"] == workername:
            if devinfo["health"] != "Retired":
                if noact:
                    print("\tNOACT: Set %s to unknow" % device["hostname"])
                else:
                    print("\tACTION: Set %s to unknow" % device["hostname"])
                    server.scheduler.devices.update(device["hostname"], None, None, None, None, 'UNKNOWN')
            else:
                print("\tSKIP: %s is retired" % device["hostname"])
    return 0

def set_worker_state(workername, state):
    server = xmlrpc.client.ServerProxy(os.environ.get("LAVAURI"), allow_none=True)
    if workername == "all":
        workerlist = server.scheduler.workers.list()
        for worker in workerlist:
            if worker == 'lava-logs':
                continue
            ret = set_worker_state(worker, state)
            if ret != 0:
                return ret
        return 0
    workerlist = server.scheduler.workers.list()
    for worker in workerlist:
        if worker == workername:
            if noact:
                print("NOACT: Set %s to %s" % (workername, state))
                return 0
            else:
                print("ACTION: Set %s to %s" % (workername, state))
                server.scheduler.workers.update(workername, None, state)
                return 0
    print("ERROR: worker %s does not exists" % workername)
    return 1



if len(sys.argv) <= 1:
    usage()
    sys.exit(1)

carg = 1
if sys.argv[carg] == "-n":
    noact = True
    carg = carg + 1

if sys.argv[carg] == "back" or sys.argv[carg] == "backfrommaintenance":
    ret = set_worker_state(sys.argv[carg + 1], "ACTIVE")
    if ret != 0:
        sys.exit(1)
    set_devices_unknown(sys.argv[carg + 1])
    print("DONE")
    sys.exit(0)
    
if sys.argv[carg] == "maint" or sys.argv[carg] == "maintenance":
    ret = set_worker_state(sys.argv[carg + 1], "MAINTENANCE")
    if ret != 0:
        sys.exit(1)
    timeout = 60
    nojob = False
    while not nojob:
        ret = check_jobs_on_worker(sys.argv[carg + 1])
        if ret == 1:
            print("There are still devices running")
            sleep(2)
            timeout = timeout - 1
        else:
            nojob = True
    print("DONE")
    sys.exit(0)

usage()
sys.exit(1)
