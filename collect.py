import argparse
from importlib import import_module

def main():
    parser = argparse.ArgumentParser(description=('Query metrics via a specified collector module'))
    parser.add_argument('-c', '--config-file', type=argparse.FileType('r'),
                        help='the YAML configuration file')
    parser.add_argument('module', help='The collector module to load')
    argv = parser.parse_args()

    config_file = argv.config_file
    config = yaml.safe_load(config_file)

    if not config:
        raise Exception('Could not load config file from {}'.format(config_file))

    module = import_module(argv.module)

    if argv.module not in config:
        raise Exception('Missing module configuration')

    module.collect(config[argv.module])

if __name__ == '__main__':
    main()
