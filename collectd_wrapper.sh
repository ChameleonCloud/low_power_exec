#!/usr/bin/env bash
command="${1:-power}"

python <<PYSCRIPT
from jinja2 import Template
from yaml import safe_load
with open('/collectd.conf.j2') as f:
  template = Template(f.read())
with open('/etc/metrics/config.yml') as f:
  config = safe_load(f)
  # Merge command-specific configuration into parent scope
  config.update(config.get('$command'))
output = template.render(config)
with open('/etc/collectd.conf', 'wb') as f:
  f.write(output + '\n')
PYSCRIPT

if [[ $? -gt 0 ]]; then
  echo "Failed to write collectd configuration."
  exit 1
fi

touch /var/log/collectd.log
chown apim: /var/log/collectd.log

exec collectd -f
