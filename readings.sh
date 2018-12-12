#!/bin/bash
# Actual collectd exec script. Configure in collectd as follows:
#
# # Load the exec plugin with an interval of 180 secconds
# <LoadPlugin exec>
#    Interval 20
# </LoadPlugin>
#
# # Add this scipt:
# <Plugin exec>
#    Exec "apim:docker" "/home/apim/collectd/readings.sh"
#        Interval 20
# </Plugin>
#
# Note that script should run as a user with access to the docker daemon.


INTERVAL="${COLLECTD_INTERVAL:-180}"

# make sure there is no container with name collectdReadings; the run below sets the --rm flag but it is 
# possible the container will be left if, for instance, docker is restarted while the container is 
# running; suppress errors as failures are expected.
docker rm -f collectdReadings &>/dev/null

# run the actual container
docker run --rm --name collectdReadings -e INTERVAL=$INTERVAL -e IDRAC_USER=$IDRAC_USER -e IDRAC_PASSWORD="moseisley" awbarnes/dell_exec
