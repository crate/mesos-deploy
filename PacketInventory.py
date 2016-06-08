#!/usr/bin/env python3

import configparser
import requests
import sys

API="https://api.packet.net/%s"

class PacketInventory(object):
    def __init__(self, apikey, projectid):
        self.hosts = []
        self.header = {'X-Auth-Token': apikey}

        req_url = "/projects/%s/devices" % projectid
        response = requests.get(url = API % req_url, headers = self.header)
        devices = response.json()['devices']
        self._get_hosts(devices)

    def _get_hosts(self, devices):
        for host in devices:
            hostname = host['hostname']
            user = host['user']
            ip = self._get_ip(host, False)
            private_ip = self._get_ip(host, False)
            self.hosts.append((hostname, user, ip,  private_ip))

    def _get_ip(self, host, is_public = True):
        retval = None
        for address in host['ip_addresses']:
            if address['public'] == is_public:
                retval = address['address']
                break
        return retval

    def _get_masters(self):
        return [host for host in self.hosts if 'master' in host[0]]

    def _get_slaves(self):
        return [host for host in self.hosts if 'slave' in host[0]]

    def _get_grafana_hosts(self):
        return [host for host in self.hosts if 'grafana' in host[0]]

    def create_inventory(self, file = 'inventory'):
        with open(file, 'w') as cfgfile:
            cfgfile.write('[mesos-masters]\n')
            for host in self._get_masters():
                cfgfile.write("%s ansible_host=%s ansible_user=%s zookeeper_id=%s private_ip=%s\n"
                              % (host[0], host[2], host[1], host[0][-1], host[3]))

            cfgfile.write('[mesos-slaves]\n')
            for host in self._get_slaves():
                cfgfile.write("%s ansible_host=%s ansible_user=%s private_ip=%s\n"
                              % (host[0], host[2], host[1], host[3]))

            cfgfile.write('[grafana-hosts]\n')
            for host in self._get_grafana_hosts():
                cfgfile.write("%s ansible_host=%s ansible_user=%s private_ip=%s\n"
                              % (host[0], host[2], host[1], host[3]))

    def create_zk(self, file = 'zk.j2'):
        content = "zk://%s/mesos"
        ips = ["%s:2181" % host[3] for host in self._get_masters()]
        zk_string = ",".join(ips)
        with open(file, 'w') as zkfile:
            zkfile.write(content % zk_string)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide the credentials file as first argument.")
        exit(1)

    with open(sys.argv[1], "r") as cr_file:
        api_key = str(cr_file.readline().strip())
        project_id = str(cr_file.readline().strip())

    inv = PacketInventory(api_key, project_id)
    inv.create_inventory()
    inv.create_zk()
