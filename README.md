# Power Collection for low-power nodes in an HP Moonshot 1500 Chassis #

## Overview ##
This project provides a Python script and associated Docker image that can be used as an exec-plugin script to
collectd to automatically collect instantaneous power usage (in wattage) and temperature readings (in Celsius) from low power nodes in an HP Moonshot 1500
 Chassis. This work is part of the ChameleonCloud project.

## Prerequisites ##
In order to make use of this script, collectd must be installed and configured on a server with SSH access to the
HP Moonshot chassis controller node.

Install and start the collectd daemon:
```
$ yum install collectd
$ service collectd start
```

Update collectd configuration (`/etc/collectd.conf`) to activate the exec plugin and
```
<LoadPlugin exec>
    Interval 20
</LoadPlugin>

<Plugin exec>
    Exec "<user>:<group>" "/path/to/power.sh"
        Interval 20
</Plugin>
```

Here, `user` should be a non-root user with execute access to the `power.sh` script (see next section).

Additionally, the `power.sh` script requires docker, and `user` must be configure with access to the docker daemon
 (e.g., be in the docker group).


## Building, Pushing and Installing the Scripts ##
Use the Dockerfile in this repository to build and push a docker image, e.g.,
```
$ docker build -t jstubbs/low_power_exec .
$ docker push jstubbs/low_power_exec
```

On the host with collectd running, pull the image:
```
$ docker pull jstubbs/low_power_exec
```

Finally, install the `power.sh` script on the collectd host and update the SSH_PASSWORD variable with the password needed
to connect to the Moonshot chassis controller node.


## Output ##
First, configure collectd with the CSV write plugin:
```
LoadPlugin csv
```

Output is written to files in the directory `/var/lib/collectd/<hostname>/exec-c<cartridge>n<node>`.


## Troubleshooting ##

Check the logs in `/var/logs/messages` to run down configuration issues and other problems with collectd.

