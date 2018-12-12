"""
Python Script for collecting power and temperature readings from dell nodes using ipmitool.
"""
import subprocess
import csv
import logging
import json
import os

def get_config_from_file():
    with open('/dell_conf.json', 'r') as f:
        conf = json.load(f)
    return conf['IDRAC_USER'], conf['INTERVAL']

def get_idrac_password_from_file():
    try:
        f = open('/idrac_password', 'r')
    except FileNotFoundError:
        logging.error('File idrac_password not found.')
    else:
        with f:
            idrac_pass = f.read()
        return idrac_pass.strip()

def execute_power_command(idrac_user,idrac_pass,idrac_host):
    args =["ipmitool", "-I", "lanplus", "-U", idrac_user, "-P", idrac_pass, "-H", idrac_host+"-oob", "dcmi", "power", "reading"]
    try:
        output = subprocess.check_output(args, timeout=2)
    except subprocess.TimeoutExpired as e:
        logging.warning('IPMI command timed out on Node %s', idrac_host)
        raise 
    except Exception as e:
       logging.warning('Error on Node %s: %s',idrac_host,e) 
    else:
        return output    

def execute_temperature_command(idrac_user,idrac_pass,idrac_host):
    args =["ipmitool", "-I", "lanplus", "-U", idrac_user, "-P", idrac_pass, "-H", idrac_host+"-oob", "dcmi", "get_temp_reading"]
    try:
        output = subprocess.check_output(args, timeout=2)
    except subprocess.TimeoutExpired as e:
        logging.warning('IPMI command timed out on Node %s', idrac_host)
        raise
    except Exception as e:
       logging.warning('Error on Node %s: %s',idrac_host,e) 
    else:
        return output    

def process_raw_output_power(output, node_name, ironic_id, interval):
    p = output.decode("utf-8")
    p = p.splitlines()
    for idx, line in enumerate(p):
        if 'Instantaneous' in str(line):
            instant_wattage = line.split(':')[1].strip(' ').split(' ')[0]
            sensor_name = line.split(':')[0].split()[1]
            push_to_collectd(node_name, ironic_id, sensor_name, interval, instant_wattage)

def process_raw_output_temperature(output, node_name, ironic_id, interval):
    p = output.decode("utf-8")
    p = p.splitlines()
    for idx, line in enumerate(p):
        if 'temperature' in str(line):
            temp_line = line.split()
            if 'Inlet' in str(line):
                sensor_name = temp_line[0] + "-" + temp_line[1]
            elif 'CPU' in str(line):
                sensor_name = temp_line[0] + "-" + temp_line[3]
            else:
                sensor_name = temp_line[0]
            reading = temp_line[4].split('+')[1] 
            push_to_collectd(node_name, ironic_id, sensor_name, interval, reading)
            
def push_to_collectd(node_name, ironic_id, sensor_name, interval, reading):
    """Use the PUTVAL command to push a temperature cosumption tuple into collectd."""
    # scripts launched by the collectd exec plugin should write values to standard out in the format specified
    # here:  http://collectd.org/documentation/manpages/collectd-exec.5.shtml
    print('PUTVAL "{}/exec-{}/gauge-{}" interval={} N:{}'.format(node_name, ironic_id, sensor_name, interval, reading))


def main():
    if os.path.exists('/dell_conf.json'):
        user, interval = get_config_from_file()
    else:
        user = os.environ.get('IDRAC_USER', 'root')
        interval = os.environ.get('INTERVAL', '180')
 
    idrac_pass = os.environ.get('IDRAC_PASSWORD')
    if not idrac_pass:
        idrac_pass = get_idrac_password_from_file()
    with open("/dell_nodes.json") as f:
        nodes = json.load(f)    
    for node_name,ironic_id in nodes.items():
        try:
            output_power = execute_power_command(user,idrac_pass,node_name)
        except:
            continue
        else:
            process_raw_output_power(output_power,node_name,ironic_id, interval)
            try:
                output_temperature = execute_temperature_command(user,idrac_pass,node_name)   
            except:
                continue
            else:
                process_raw_output_temperature(output_temperature,node_name,ironic_id, interval)
    
if __name__ == '__main__':
    main()

