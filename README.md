# Power Collection for Dell nodes in the Chameleon Testbed #

## Overview ##
This project provides a Python script and associated Docker image that can be used as an exec-plugin script to
collectd to automatically collect instantaneous power usage (in wattage) and temperature readings (in Celsius) from Dell nodes. This work is part of the ChameleonCloud project.

## Prerequisites ##
In order to make use of this script, collectd must be installed and configured on a server with ipmitool and out-of-band access to the nodes.

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
    Exec "<user>:<group>" "/path/to/readings.sh"
        Interval 20
</Plugin>
```

Here, `user` should be a non-root user with execute access to the `readings.sh` script (see next section).

Additionally, the `readings.sh` script requires docker, and `user` must be configure with access to the docker daemon
 (e.g., be in the docker group).


## Building, Pushing and Installing the Scripts ##
Use the Dockerfile in this repository to build and push a docker image, e.g.,
```
$ docker build -t awbarnes/dell_collectd .
$ docker push awbarnes/dell_collectd
```

On the host with collectd running, pull the image:
```
$ docker pull awbarnes/dell_collectd
```

Finally, install the `readings.sh` script on the collectd host and update the IDRAC_PASSWORD variable with the password needed
to connect to the Dell nodes.


## Output ##
First, configure collectd with the CSV write plugin:
```
LoadPlugin csv
```

Output is written to files in the directory `/var/lib/collectd/<hostname>/exec-<node-id>`.


## Troubleshooting ##

Check the logs in `/var/logs/messages` to run down configuration issues and other problems with collectd.

