#!/bin/bash
# Actual collectd exec script. Configure in collectd as follows:
#
# # Load the exec plugin with an interval of 20 secconds
# <LoadPlugin exec>
#    Interval 20
# </LoadPlugin>
#
# # Add this scipt:
# <Plugin exec>
#    Exec "apim:docker" "/home/apim/collectd/power.sh"
#        Interval 20
# </Plugin>
#
# Note that script should run as a user with access to the docker daemon.


HOSTNAME="${COLLECTD_HOSTNAME:-localhost}"
INTERVAL="${COLLECTD_INTERVAL:-60}"

# make sure there is no container with name collectdPower; the run below sets the --rm flag but it is 
# possible the container will be left if, for instance, docker is restarted while the container is 
# running; suppress errors as failures are expected.
docker rm -f collectdPower &>/dev/null

# run the actual container
docker run --rm --name collectdPower -e HOSTNAME=$HOSTNAME -e INTERVAL=$INTERVAL -e SSH_PASSWORD=<the_password> jstubbs/low_power_exec
