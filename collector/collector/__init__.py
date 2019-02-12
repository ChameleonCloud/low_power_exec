import argparse
from importlib import import_module
from yaml import safe_load

def main():
    parser = argparse.ArgumentParser(description=('Query metrics via a specified collector module'))
    parser.add_argument('-c', '--config-file', type=argparse.FileType('r'),
                        help='the YAML configuration file')
    parser.add_argument('module', help='The collector module to load')
    argv = parser.parse_args()

    config_file = argv.config_file
    config = safe_load(config_file)

    if not config:
        raise Exception('Could not load config file from {}'.format(config_file))

    module = import_module('.{}'.format(argv.module), package='collector')

    if argv.module not in config:
        raise Exception('Missing module configuration')

    module.collect(config[argv.module])
