#!/bin/bash

# start collectd
exec collectd

tail -f /dev/null
