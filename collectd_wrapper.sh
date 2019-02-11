#!/usr/bin/env bash
command="${1:-power}"
user=apim

config_path=/etc/metrics/config.yml
logs_path=/var/log/collectd.log
# Create a copy of the metrics; we are going to be changing the ownership
# so that the plugin code can read this as configuration.
tmp_config_path=$(mktemp --tmpdir metrics-config.XXXXXX.yml)
cat $config_path >$tmp_config_path && chown $user: $tmp_config_path
touch $logs_path && chown $user: $logs_path

python <<PYSCRIPT
from jinja2 import Template
from yaml import safe_load
with open('/collectd.conf.j2') as f:
  template = Template(f.read())
with open('$tmp_config_path') as f:
  config = safe_load(f)
  # Merge command-specific configuration into parent scope
  config.update(config.get('$command'))
  # Template out name of config file
  config.update(config_file='$tmp_config_path')
output = template.render(config)
with open('/etc/collectd.conf', 'wb') as f:
  f.write(output + '\n')
PYSCRIPT

if [[ $? -gt 0 ]]; then
  echo "Failed to write collectd configuration."
  exit 1
fi

exec collectd -f
