"""
Python script to collect power usage (in wattage) and temperature readings (in celsius) from low-power nodes in an HP Moonshot 1500 Chassis using
iLO commands over SSH to the chassis controller.
"""
import json
import logging
import os
import sys
from paramiko import SSHClient, AutoAddPolicy
from timeit import default_timer as timer

LOG = logging.getLogger(__name__)

def execute_power_command(ssh, command='show cartridge power all'):
    """Execute the iLO power command to collect power data over an `ssh` connection to the chassis controller."""
    _, ssh_stdout, _ = ssh.exec_command(command)
    return ssh_stdout.read()

def execute_temperature_command(ssh, command='show cartridge temperature all'):
    """Execute the iLO temperature command to collect temperature data over an `ssh` connection to the chassis controller."""
    _, ssh_stdout, _ = ssh.exec_command(command)
    return ssh_stdout.read()

def get_ironic_id(node_cartridge_code):
    """Convert the hostname to an ironic id"""
    with open('/ironic_ids.json', 'r') as f:
        low_power_ironic_ids = json.load(f)
        node_name = 'c10-{}'.format(node_cartridge_code)
        if not node_name in low_power_ironic_ids:
            raise ValueError('Missing node name {} in Ironic node configuration'.format(node_name))
        return low_power_ironic_ids['c10-{}'.format(node_cartridge_code)]

def push_to_collectd_power(node_name, node_cartridge_code, instant_wattage, hostname):
    """Use the PUTVAL command to push a power cosumption tuple into collectd."""
    LOG.debug("Top of push_to_collectd_power for node_name: {} and instant_wattage: {}".format(node_name, instant_wattage))
    ironic_id = get_ironic_id(node_cartridge_code)
    # scripts launched by the collectd exec plugin should write values to standard out in the format specified
    # here:  http://collectd.org/documentation/manpages/collectd-exec.5.shtml
    print('PUTVAL "{}/exec-{}/gauge-power" N:{}'.format(hostname, ironic_id, instant_wattage))
    # print('PUTVAL "{}" N:{}'.format(node_cartridge_code, instant_wattage))

def push_to_collectd_temperature(node_name, node_cartridge_code, instant_temperature, hostname):
    """Use the PUTVAL command to push a temperature cosumption tuple into collectd."""
    LOG.debug("Top of push_to_collectd_temperature for node_name: {} and instant_temperature: {}".format(node_name, instant_temperature))
    ironic_id = get_ironic_id(node_cartridge_code)
    # scripts launched by the collectd exec plugin should write values to standard out in the format specified
    # here:  http://collectd.org/documentation/manpages/collectd-exec.5.shtml
    print('PUTVAL "{}/exec-{}/gauge-temperature_cpu" N:{}'.format(hostname, ironic_id, instant_temperature))

def process_raw_output_power(output, hostname):
    """Parse the raw output from the power command and issue PUTVAL commands to push data to collectd."""
    LOG.debug("parsing raw power output.")
    r = output.splitlines()
    for idx, line in enumerate(r):
        # each line that contains "#Cartridge" starts a new block of lines representing a node reading.
        if '#Cartridge' in str(line):
            # the wattage line is the third line after the new block:
            watt_line = r[idx+3].decode("utf-8")
            try:
                instant_wattage = watt_line.split('Instant Wattage:')[1].strip().split(' ')[0]
            except IndexError:
                LOG.error("Unable to parse instant wattage - 'Instant Wattage:' not found in watt_line: {}".format(watt_line))
            except Exception as e:
                LOG.error("Unable to parse instant wattage - unexpected error: {} parsing watt_line: {}".format(e, watt_line))
            # the node line is the fourth line after the new block.
            node_line = r[idx+4].decode("utf-8")
            node_cartridge_code = node_line.split(":")[0].strip()
            node_name = node_line.split(":")[1].strip()
            push_to_collectd_power(node_name, node_cartridge_code, instant_wattage, hostname)

def process_raw_output_temperature(output, hostname):
    """Parse the raw output from the temperature command and issue PUTVAL commands to push data to collectd."""
    LOG.debug("parsing raw thermal output.")
    r = output.splitlines()
    #data = dict()
    for idx, line in enumerate(r):
        # Collect every cartridge number for a key value.
        if '#Cartridge' in str(line):
            cart_line = r[idx].decode("utf-8")
            cart_num =  cart_line.split(':')[0]
        # We are only collecting the CPU temperature at this moment (Temp Sensor 2)
        elif 'Temperature Sensor 2:' in str(line):
            temp_line = r[idx+3].decode("utf-8")
            try:
                instant_temperature = temp_line.split(':')[1].strip().split()[0]
            except IndexError:
                LOG.error("Unable to parse instant temperature - 'Temperature Sensor 2:'' not found in temp_line: {}".format(temp_line))
            except Exception as e:
                LOG.error("Unable to parse instant temperature - unexpected error: {} parsing temp_line: {}".format(tem_line))
            sensor_line = r[idx+1].decode("utf-8")
            try:
                sensor_name = sensor_line.split(':')[1].strip()
            except IndexError:
                LOG.error("Unable to parse sensor name - 'Temperature Sensor 2:'' not found in sensor_line: {}".format(sensor_line))
            except Exception as e:
                LOG.error("Unable to parse sensor name - unexpected error: {} parsing sensor_line: {}".format(sensor_line))
            cart_code = cart_num + "n1"
            node_name = cart_line.split(":")[1].strip()
            if (instant_temperature != 'N/A'):
                push_to_collectd_temperature(node_name, cart_code, instant_temperature, hostname)

            # TODO: Create a dictionary with the key of a sensor name and the reading as a value
            #sensor_dict = dict()
            #sensor_dict = {sensor_name : instant_temperature}
            #data = {cart_num : sensor_dict}
            #       print(data)


def collect(config):
    timers = [timer()]

    ip = config.ip
    ssh_user = config.ssh_user
    ssh_password = config.ssh_password
    hostname = config.hostname
    interval = config.interval
    debug = getattr(config, 'debug', False)

    if debug:
        logging.basicConfig(level=logging.DEBUG)

    try:
        LOG.debug("obtaining an SSH connection.")
        with SSHClient() as ssh:
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(ip, username=ssh_user, password=ssh_password)
            timers.append(timer())

            output_power = execute_power_command(ssh)
            timers.append(timer())

            output_temperature = execute_temperature_command(ssh)
            timers.append(timer())

            process_raw_output_power(output_power, HOSTNAME, INTERVAL)
            process_raw_output_temperature(output_temperature, HOSTNAME, INTERVAL)
            timers.append(timer())
    except paramiko.AuthenticationException as e:
    except paramiko.SSHException as e:
    except Exception as e:

        # TODO: write timing data
