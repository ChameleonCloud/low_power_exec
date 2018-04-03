# Parse the TIME_RESULTS_FILE to determine basic run time characteristics of the exec plugin script.
# Requires: Python 3.4+
# Can run this script in the low_power_exec container using a command such as the following:
# docker run -it --rm -v /home/apim/collectd/time_results.csv:/time_results.csv --entrypoint=ipython jstubbs/low_power_exec:0.2

import os
from statistics import *

times_file = os.environ.get('TIME_RESULTS_FILE', '/time_results.csv')

# create a list of the times data:
with open(times_file, 'r') as f:
    content = f.readlines()
lines =  [x.strip() for x in content]

# create a list of the total run times, given by the last value in each row:
times = []
for l in lines:
    times.append(float(l.split(',')[7]))

print("Total runs: {}".format(len(times)))
print("Mean: {}".format(mean(times)))
print("Median: {}".format(median(times)))
print("Standard Devition: {}".format(stdev(times)))

# collect the actual time