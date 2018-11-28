"""
Python Script for collecting power and temperature readings from dell nodes using ipmitool.
"""
import subprocess
import csv

def get_config_from_file():
    with open('/dell_conf.json', 'r') as f:
        conf = json.load(f)
    return conf['IDRAC_USER'], conf['TESTING'], conf['HOSTNAME'], conf['INTERVAL'], conf['WRITE_TIME_RESULTS']

def get_idrac_password_from_file():
    with open('/idrac_password', 'r') as f:
        idrac_password = f.read()
    return idrac_password.strip()

def get_ironic_id(node_name):
    """Convert the nodename to an ironic id"""
    with open('/dell_nodes.json', 'r') as f:
        dell_nodes = json.load(f)
    try:
        return dell_nodes[node_name]
    except KeyError:
        print("Unexpected node_name: {}".format(node_name))
        sys.exit()

def execute_power_command(idrac_user,idrac_pass,idrac_ip)
    try:
        args =["ipmitool", "-I", "lanplus", "-U", idrac_user, "-P", idrac_pass, "-H", idrac_ip, "dcmi", "power", "reading"]
        output = subprocess.check_output(args)
    except Exception as e:
        print("Unable to execute ipmitool command: {}".format(e))
        sys.exit()
    return output    

def execute_temperature_command(idrac_user,idrac_pass,idrac_ip)
    try:
        args =["ipmitool", "-I", "lanplus", "-U", idrac_user, "-P", idrac_pass, "-H", idrac_ip, "dcmi", "get_temp_reading"]
        output = subprocess.check_output(args)
    except Exception as e:
        print("Unable to execute ipmitool command: {}".format(e))
        sys.exit()
    return output    

def process_raw_output_power(output, node_id, testing)
    p = output.decode("utf-8")
    p = p.splitlines()
    for idx, line in enumerate(p):
        if 'Watts' in str(line):
            watt_line = p[idx]
            try:
                instant_wattage = watt_line.split(':')[1].strip(' ').split(' ')[0]
                if testing:
                    sensor_name = watt_line.split(':')[0].strip()
                    print("{} : {}".format(sensor_name, instant_wattage))
            except IndexError:
                print("Unable to parse instant wattage - 'Instant Wattage:' not found in watt_line: {}".format(watt_line))
            except Exception as e:
                print("Unable to parse instant wattage - unexpected error: {} parsing watt_line: {}".format(e, watt_line))
            push_to_collectd_power(instant_wattage, interval, node_name, testing)

def process_raw_output_temperature(output, testing)
    p = output.decode("utf-8")
    p = p.splitlines()
    for idx, line in enumerate(p):
        if 'temperature' in str(line):
            try:
                temp_line = line.split()
                sensor_name = temp_line[0] + "_" + temp_line[1]
                temp_reading = temp_line[4].split('+')[1]
                if testing:
                    print("{}: {}".format(sensor_name, temp_reading))
            except Exception as e:
                print("Unable to parse for temperature - unexpected error: {} parsing temp_line: {}".format(e, temp_line))
            push_to_collectd_temperature(temp_reading, sensor_name, interval, node_name, testing)
            
def push_to_collectd_temperature(temp_reading, sensor_name, interval, node_name, testing=False):
    """Use the PUTVAL command to push a temperature cosumption tuple into collectd."""
    if testing:
        print("Top of push_to_collectd_temperature for node_name: {} and instant_temperature: {}".format(node_name, instant_temperature))
    ironic_id = get_ironic_id(node_cartridge_code)
    # scripts launched by the collectd exec plugin should write values to standard out in the format specified
    # here:  http://collectd.org/documentation/manpages/collectd-exec.5.shtml
    print('PUTVAL "{}/exec-{}/gauge-temperature_cpu" interval={} N:{}'.format(hostname, ironic_id, interval, instant_temperature))

def main()
    if os.path.exists('/dell_conf.json'):
        USER, TESTING, INTERVAL = get_config_from_file()
    else:
        USER = os.environ.get('USER', 'root')
        TESTING = os.environ.get('TESTING', 'False') 
        INTERVAL = os.environ.get('INTERVAL', '1')
        
    if TESTING:
        NODE = os.environ.get('NODE', '172.16.109.6')
    get_idrac_password_from_file()            
    output_power = execute_power_command(USER,idrac_pass,NODE)
    output_temperature = execute_temperature_command(USER,idrac_pass,NODE)   
    
    
#[root@dev low_power_exec]# ipmitool -I lanplus -U root -P moseisley -H c07-32-oob dcmi get_temp_reading
#
#        Entity ID                       Entity Instance    Temp. Readings
#Inlet air temperature(40h)                      1               +19 C
#CPU temperature sensors(41h)                    1               +59 C
#CPU temperature sensors(41h)                    2               +54 C
#Baseboard temperature sensors(42h)              1               +40 C
