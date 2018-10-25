"""
Python script to collect power usage (in wattage) from low-power nodes in an HP Moonshot 1500 Chassis using
iLO commands over SSH to the chassis controller.
"""
import json
import os
import sys
import paramiko
import timeit

def get_config_from_file():
    with open('/low_power_conf.json', 'r') as f:
        conf = json.load(f)
    return conf['SSH_USER'], conf['TESTING'], conf['HOSTNAME'], conf['INTERVAL'], conf['WRITE_TIME_RESULTS']

def get_ssh_password_from_file():
    with open('/ssh_password', 'r') as f:
        ssh_password = f.read()
    return ssh_password.strip()

def get_ssh_connection(ip, username, password):
    """Make an ssh connection to `ip` with `username` and `password`."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    try:
        ssh.connect(ip, username=username, password=password)
    except paramiko.AuthenticationException as e:
        print("Unable to create SSH connection: invalid authentication credentials. Exception: {}".format(e))
        sys.exit()
    except paramiko.SSHException as e:
        print("Unable to create SSH connection: error connecting or establishing connection. Exception: {}".format(e))
        sys.exit()
    except Exception as e:
        print("Unable to create SSH connection: unknown error. Exception: {}".format(e))
        sys.exit()
    return ssh

def execute_power_command(ssh, command='show cartridge power all'):
    """Execute the iLO power command to collect power data over an `ssh` connection to the chassis controller."""
    try:
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
        output = ssh_stdout.read()
    except paramiko.SSHException as e:
        print("Unable to execute command over SSH: error connecting or establishing connection. Exception: {}".format(e))
        ssh.close()
        sys.exit()
    except Exception as e:
        print("Unable to execute command over SSH: unknown error. Exception: {}".format(e))
        ssh.close()
        sys.exit()
    return output

def execute_temperature_command(ssh, command='show cartridge temperature all'):
    """Execute the iLO temperature command to collect temperature data over an `ssh` connection to the chassis controller."""
    try:
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
        output = ssh_stdout.read()
    except paramiko.SSHException as e:
        print("Unable to execute command over SSH: error connecting or establishing connection. Exception: {}".format(e))
        ssh.close()
        sys.exit()
    except Exception as e:
        print("Unable to execute command over SSH: unknown error. Exception: {}".format(e))
        ssh.close()
        sys.exit()
    return output

def get_ironic_id(node_cartridge_code):
    """Convert the hostname to an ironic id"""
    with open('/ironic_ids.json', 'r') as f:
        low_power_ironic_ids = json.load(f)
    try:
        return low_power_ironic_ids['c10-{}'.format(node_cartridge_code)]
    except KeyError:
        print("Unexpected node_cartridge_code: {}".format(node_cartridge_code))
        sys.exit()

def push_to_collectd(node_name, node_cartridge_code, instant_wattage, hostname, interval, testing=False):
    """Use the PUTVAL command to push a power cosumption tuple into collectd."""
    if testing:
        print("Top of push_to_collectd for node_name: {} and instant_wattage: {}".format(node_name, instant_wattage))
    ironic_id = get_ironic_id(node_cartridge_code)
    # scripts launched by the collectd exec plugin should write values to standard out in the format specified
    # here:  http://collectd.org/documentation/manpages/collectd-exec.5.shtml
    print('PUTVAL "{}/exec-{}/gauge-power" interval={} N:{}'.format(hostname, ironic_id, interval, instant_wattage))
    # print('PUTVAL "{}" N:{}'.format(node_cartridge_code, instant_wattage))

def push_to_collectd_temperature(node_name, node_cartridge_code, instant_temperature, hostname, interval, testing=False):
    """Use the PUTVAL command to push a temperature cosumption tuple into collectd."""
    if testing:
        print("Top of push_to_collectd for node_name: {} and instant_temperature: {}".format(node_name, instant_temperature))
    ironic_id = get_ironic_id(node_cartridge_code)
    # scripts launched by the collectd exec plugin should write values to standard out in the format specified
    # here:  http://collectd.org/documentation/manpages/collectd-exec.5.shtml
    print('PUTVAL "{}/exec-{}/temperature-cpu" interval={} N:{}'.format(hostname, ironic_id, interval, instant_temperature))

def process_raw_output_power(output, hostname, interval, testing=False):
    """Parse the raw output from the power command and issue PUTVAL commands to push data to collectd."""
    r = output.splitlines()
    for idx, line in enumerate(r):
        # each line that contains "#Cartridge" starts a new block of lines representing a node reading.
        if '#Cartridge' in str(line):
            # the wattage line is the third line after the new block:
            watt_line = r[idx+3].decode("utf-8")
            try:
                instant_wattage = watt_line.split('Instant Wattage:')[1].strip().split(' ')[0]
            except IndexError:
                print("Unable to parse instant wattage - 'Instant Wattage:' not found in watt_line: {}".format(watt_line))
            except Exception as e:
                print("Unable to parse instant wattage - unexpected error: {} parsing watt_line: {}".format(e, watt_line))
            # the node line is the fourth line after the new block.
            node_line = r[idx+4].decode("utf-8")
            node_cartridge_code = node_line.split(":")[0].strip()
            node_name = node_line.split(":")[1].strip()
            push_to_collectd(node_name, node_cartridge_code, instant_wattage, hostname, interval, testing)

def process_raw_output_temperature(output, hostname, interval, testing=False):
    """Parse the raw output from the temperature command and issue PUTVAL commands to push data to collectd."""
    r = output.splitlines()
    #data = dict()
    for idx, line in enumerate(r):
        # Collect every cartridge number for a key value.
        if '#Cartridge' in str(line):
            cart_num =  line.split(':')[1].replace('#', '')
        # We are only collecting the CPU temperature at this moment (Temp Sensor 2)
        elif 'Temperature Sensor 2:' in str(line):
            try:
                instant_temperature = (r[idx+3]).split(':')[1].strip().split()[0]
            except IndexError:
                print("Unable to parse instant temperature - 'Temperature Sensor 2:'' not found in r[idx+1]: {}".format(r[idx+1]))
            except Exception as e:
                print("Unable to parse instant temperature - unexpected error: {} parsing r[idx+1]: {}".format(r[idx+1]))
            try:
                sensor_name = (r[idx+1]).split(':')[1].strip()
            except IndexError:
                 print("Unable to parse sensor name - 'Temperature Sensor 2:'' not found in r[idx+3]: {}".format(r[idx+3]))
            except Exception as e:
                print("Unable to parse sensor name - unexpected error: {} parsing r[idx+3]: {}".format(r[idx+3]))    
            cart_code = "c" + cart_num + "n1"
            if (instant_temperature != 'N/A'):
                push_to_collectd_temperature(cart_code, instant_temperature, hostname, interval, testing)
            
            # TODO: Create a dictionary with the key of a sensor name and the reading as a value
            #sensor_dict = dict()
            #sensor_dict = {sensor_name : instant_temperature}
            #data = {cart_num : sensor_dict}
            #       print(data)
             
            

def main():
    time_0 = timeit.default_timer()
    IP = os.environ.get('IP', '172.16.109.218')
    if os.path.exists('/low_power_conf.json'):
        SSH_USER, TESTING, HOSTNAME, INTERVAL, WRITE_TIME_RESULTS = get_config_from_file()
    else:
        SSH_USER = os.environ.get('SSH_USER', 'Administrator')
        TESTING = os.environ.get('TESTING', 'False')
        HOSTNAME = os.environ.get('HOSTNAME', 'localhost')
        INTERVAL = os.environ.get('INTERVAL', '1')
        WRITE_TIME_RESULTS = os.environ.get('WRITE_TIME_RESULTS', 'False')

    SSH_PASSWORD = os.environ.get('SSH_PASSWORD')
    if not SSH_PASSWORD:
        SSH_PASSWORD = get_ssh_password_from_file()
    write_time_results = WRITE_TIME_RESULTS == 'True'
    if write_time_results:
        TIME_RESULTS_FILE = os.environ.get('TIME_RESULTS_FILE', 'time_results.csv')
    testing = TESTING == 'True'
    if write_time_results:
        print("writing time results to: {}".format(TIME_RESULTS_FILE))

    if not SSH_PASSWORD:
        print("Missing SSH_PASSWORD. Script exiting.")
    if testing:
        print("obtaining an SSH connection.")
    ssh = get_ssh_connection(IP, SSH_USER, SSH_PASSWORD)
    if testing:
        print("SSH connection obtained. executing commands.")
    time_1 = timeit.default_timer()
    output_power = execute_power_command(ssh)
    time_2 = timeit.default_timer()
    output_temperature = execute_temperature_command(ssh)
    time_3 = timeit.default_timer()
    if testing:
        print("command executed. parsing raw power output.")
    process_raw_output_power(output_power, HOSTNAME, INTERVAL, testing)
    time_4 = timeit.default_timer()
    ssh.close()
    if write_time_results:
        with open(TIME_RESULTS_FILE, 'a') as f:
            f.write('{},{},{},{},{},{},{},{},{},{}\n'.format(time_0, time_1, time_2, time_3, time_4, time_1-time_0, time_2-time_1, time_3-time_2, time_4-time_3, time_4-time_0))

if __name__ == '__main__':
    main()
