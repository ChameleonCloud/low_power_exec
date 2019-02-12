import logging
import os
import requests
import json
import time

LOG = logging.getLogger(__name__)

metric_template = 'PUTVAL "{host}/corsa/{type}-{type_instance}" {timestamp}:{value}'

class CorsaClient():
    def __init__(self, address, token, name=None, verify=None):
        self.address = address
        self.token = token
        self.verify = verify
        self.api_base = '/api/v1'

        if name:
            self.name = name
        else:
            self.name = address

    def get_path(self, path):
        headers = {'Authorization': self.token}
        url = '{}{}{}'.format(self.address, self.api_base, path)
        resp = requests.get(url, headers=headers, verify=self.verify)
        return resp.json()

    # GET STATS PORTS
    #   200 OK
    def get_stats_ports(self, port=None):
        path = '/stats/ports'
        if port:``
            path = path + '?port=' + str(port)
        return self.get_path(path)

    # GET STATS TUNNELS
    #   200 OK
    def get_stats_tunnels(self, bridge=None, ofport=None):
        path = '/stats/tunnels'
        if bridge:
            path = path + '?bridge=br' + str(bridge)
            if ofport:
                path = path + '&ofport=' + str(ofport)
        return self.get_path(ep_stats + '/tunnels')

CORSA_TO_COLLECTD_TYPE_MAP = {
    'tx_packets': 'if_tx_packets',
    'tx_errors': 'if_tx_errors',
    'tx_bytes': 'if_tx_octets',
    'tx_dropped': 'if_tx_dropped',
    'rx_packets': 'if_rx_packets',
    'rx_errors': 'if_rx_errors',
    'rx_bytes': 'if_rx_octets',
    'rx_dropped': 'if_rx_dropped'
}

def collect(config):
    switches = config['switches']
    clients = []

    for switch in switches:
        address = switch.get('address')
        token = switch.get('token')
        name = switch.get('name')
        verify = switch.get('ssl_verify', True)
        clients.append(CorsaClient(address, token, name=name, verify=verify))

    for client in clients:
        port_stats = client.get_stats_ports()
        for stat in port_stats['stats']:
            for key, val in stat.items():
                if key not in CORSA_TO_COLLECTD_TYPE_MAP:
                    continue

                print(metric_template.format(
                    host=client.name,
                    type=CORSA_TO_COLLECTD_TYPE_MAP[key],
                    type_instance=stat['port'],
                    timestamp=int(time.time()),
                    value=val
                ))
