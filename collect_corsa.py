#!/usr/bin/env python

import ConfigParser
import logging
import requests
import json
import time

LOG = logging.getLogger(__name__)

ep_datapath = '/datapath'    # Datapath
ep_stats = '/stats'          # Stats
ep_equipment = '/equipment'  # Equipment
ep_qp = '/queue-profiles'    # Queue-profiles
ep_ports = '/ports'          # Ports
ep_netns = '/netns'

metric_template = 'PUTVAL "{host}/corsa-{section}/{port}-{metric}" {timestamp}:{value}'


class CorsaClient():
    def __init__(self, address, token, verify=None):
        self.address = address
        self.token = token
        self.verify = verify
        self.api_base = '/api/v1'

    def get_path(self, path):
        headers = {'Authorization': self.token}
        url = '{}{}{}'.format(self.address, self.api_base, path)
        resp = requests.get(url, headers=headers, verify=self.verify)
        return resp.json()

    # GET DATAPATH
    #   200 OK
    #   303 See Other
    def get_datapath(self):
        return self.get_path('/datapath')

    # GET DATAPATH LAG-HASH
    #   200 OK
    def get_datapath_lag_hash(self):
        return self.get_path('/datapath/lag-hash')

    # GET DATAPATH STATUS
    #   200 OK
    #   303 See other
    def get_datapath_status(self):
        return self.get_path('/datapath/status')

    # GET EQUIPMENT
    #   200 OK
    def get_equipment(self):
        return self.get_path(ep_equipment)

    # GET EQUIPMENT SLOTS
    #   200 OK

    def get_equipment_slots(self):
        return self.get_path(ep_equipment + '/slots')

    # GET EQUIPMENT SLOT
    #   200 OK

    def get_equipment_slot(self, slot):
        return self.get_path(ep_equipment + '/slots/' + str(slot))

    # GET EQUIPMENT SLOT MODULE
    #   200 OK
    #   404 Not Found

    def get_equipment_slot_module(self, slot):
        return self.get_path(ep_equipment + '/slots/' + str(slot) + '/module')

    # GET EQUIPMENT FANTRAYS
    #   200 OK

    def get_equipment_fantrays(self):
        return self.get_path(ep_equipment + '/fantrays')

    # GET EQUIPMENT FANTRAY
    #   200 OK
    #   404 Not Found

    def get_equipment_fantray(self, fantray):
        return self.get_path(ep_equipment + '/fantrays/' + str(fantray))

    # GET EQUIPMENT FANS
    #   200 OK
    #   404 Not Found

    def get_equipment_fans(self, fantray):
        return self.get_path(ep_equipment + '/fantrays/' + str(fantray) + '/fans')

    # GET EQUIPMENT FAN
    #   200 OK
    #   404 Not Found

    def get_equipment_fan(self, fantray, fan):
        path = ep_equipment + '/fantrays/' + \
            str(fantray) + '/fans/' + str(fan)

        return self.get_path(path)

    # GET EQUIPMENT LED
    #   200 OK

    def get_equipment_led(self):
        return self.get_path(ep_equipment + '/led')

    # GET EQUIPMENT BOARDTEMP
    #   200 OK

    def get_equipment_boardtemp(self):
        return self.get_path(ep_equipment + '/boardtemp')

    # GET EQUIPMENT CPU
    #   200 OK

    def get_equipment_cpu(self):
        return self.get_path(ep_equipment + '/cpu')

    # GET EQUIPMENT PSUS
    #   200 OK

    def get_equipment_psus(self):
        return self.get_path(ep_equipment + '/psus')

    # GET EQUIPMENT PSU
    #   200 OK

    def get_equipment_psu(self, psu):
        return self.get_path(ep_equipment + '/psus/' + str(psu))

    # GET EQUIPMENT EEPROMS
    #   200 OK

    def get_equipment_eeproms(self):
        return self.get_path(ep_equipment + '/eeproms')

    # GET EQUIPMENT EEPROM
    #   200 OK

    def get_equipment_eeprom(self, eeprom):
        return self.get_path(ep_equipment + '/eeproms/' + str(eeprom))

    # GET EQUIPMENT AIRFLOW
    #   200 OK

    def get_equipment_airflow(self):
        return self.get_path(ep_equipment + '/airflow')

    # GET NETNS
    #   200 OK

    def get_netns_info(self):
        return self.get_path(ep_netns)

    # GET NETNS SPECIFIC
    #   200 OK

    def get_netns(self, netns):
        return self.get_path(ep_netns + '/' + str(netns))

    # GET NETNS TUNNELS
    #   200 OK

    def get_netns_tunnels(self, netns):
        return self.get_path(ep_netns + '/' + str(netns) + '/tunnels')

    # GET NETNS TUNNEL
    #   200 OK

    def get_netns_tunnel(self, netns, tunnel):
        return self.get_path(ep_netns + '/' + str(netns) + '/tunnels/' + str(tunnel))

    # GET PORTS
    #   200 OK
    #   403 Forbidden

    def get_ports(self):
        return self.get_path(ep_ports)

    # GET PORT
    #   200 OK
    #   403 Forbidden

    def get_port(self, port):
        return self.get_path(ep_ports + '/' + str(port))

    # GET PORT TRAFFIC CLASSES
    #   200 OK
    #   403 Forbidden

    def get_port_traffic_class(self, port):
        return self.get_path(ep_ports + '/' + str(port) + '/traffic-classes')

    # GET QUEUE PROFILES
    #   200 OK

    def get_queue_profiles(self):
        return self.get_path(ep_qp)

    # GET STATS
    #   200 OK

    def get_stats(self):
        return self.get_path(ep_stats)

    # GET STATS PORTS
    #   200 OK
    def get_stats_ports(self, port=None):
        path = ep_stats + '/ports'
        if port:
            path = path + '?port=' + str(port)
        return self.get_path(path)

    # GET STATS TUNNELS
    #   200 OK
    def get_stats_tunnels(self, bridge=None, ofport=None):
        path = ep_stats + '/tunnels'
        if bridge:
            path = path + '?bridge=br' + str(bridge)
            if ofport:
                path = path + '&ofport=' + str(ofport)
        return self.get_path(ep_stats + '/tunnels')


def main():
    config = ConfigParser.ConfigParser()
    config.read('/etc/metrics/metrics.conf')

    section_header = 'corsa:'
    sections = [s for s in config.sections() if s.startswith(section_header)]

    if not sections:
        raise ValueError(
            'Could not find any valid sections describing switches')

    for section in sections:
        identifier = section.replace(section_header, '')
        address = config.get('corsa', 'address')
        token = config.get('corsa', 'token')
        verify = config.get('corsa', 'ssl_verify')
        client = CorsaClient(address, token, verify=verify)

        try:
            port_stats = client.get_stats_ports()
            for stat in port_stats['stats']:
                for key, val in stat.items():
                    print(metric_template.format(
                        host='test',
                        section=section,
                        port=stat['port'],
                        metric=key,
                        timestamp=int(time.time()),
                        value=val
                    ))


if __name__ == '__main__':
    main()
