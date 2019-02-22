#!/usr/bin/env bash
set -e -u

module="${1:-}"
user=apim

if [[ -z "$module" ]]; then
  cat <<USAGE
Usage: $0 [MODULE]

Runs collector MODULE in a separate collectd process.
Valid collectors can be found in the python 'collector' module.

Example:
  # Run the 'switch_corsa' collector
  $0 switch_corsa
USAGE
  exit 1
fi

config_path=/etc/metrics/config.yml
logs_path=/var/log/collectd.log
collectd_conf_path=/etc/collectd.conf
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
  # Merge module-specific configuration into parent scope
  config.update(config.get('$module'))
  # Add in some information for the loader
  config.update(module_name='$module', config_file='$tmp_config_path')
output = template.render(config)
with open('$collectd_conf_path', 'wb') as f:
  f.write(output + '\n')
PYSCRIPT

if [[ $? -gt 0 ]]; then
  echo "Failed to write collectd configuration."
  exit 1
else

echo "Wrote collectd configuration to $collectd_conf_path."
exec collectd -f
