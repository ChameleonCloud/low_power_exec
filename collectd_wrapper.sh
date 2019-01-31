#!/usr/bin/env bash
config="${1:collect_power}"
ln -s "/etc/collectd.d/available/$config.conf" "/etc/collectd.d/enabled/$config.conf"

exec collectd -f
