# lava-docker upgrade/maintaince guide

## How to upgrade/maintance a slave worker

### Put the worker in maintainance
See https://validation.linaro.org/static/docs/v2/scheduler.html

Either via the web interface or via:
```
lavalab-cli workername maintainance
```

### Ensure there are no build running on slave's devices
You need to ensure that the worker have no running jobs.
lavalab-cli should handle this for you by waiting until all jobs are terminated.

### Stop the worker
You can stop the docker container or stop the lava-slave process in the container.
Note that lava-master ignore any lava-slave set as maintaince, so stopping is not mandatory.

### Upgrade/maintaince the worker


### Restart it
The lava-docker slave setup will re set the lab as working.

TODO: All devices will be kept as maintainance, by the lava-docker slave setup.
You can use as a workaround:
```
lavalab-cli workername backfrommaintainance
```
