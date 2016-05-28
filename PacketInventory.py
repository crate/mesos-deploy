#!/usr/bin/env python3

import configparser, requests

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
            ip = self._get_ip(host)
            self.hosts.append((hostname, user, ip))

    def _get_ip(self, host):
        retval = None
        for address in host['ip_addresses']:
            if address['public'] == True:
                retval = address['address']
                break
        return retval

    def _get_masters(self):
        return [host for host in self.hosts if 'master' in host[0]]

    def _get_slaves(self):
        return [host for host in self.hosts if 'slave' in host[0]]

    def create_inventory(self, file = 'inventory'):
        with open(file, 'w') as cfgfile:
            cfgfile.write('[mesos-masters]\n')
            for host in self._get_masters():
                cfgfile.write("%s ansible_host=%s ansible_user=%s zookeeper_id=%s\n"
                              % (host[0], host[2], host[1], host[0][-1]))
            cfgfile.write('[mesos-slaves]\n')
            for host in self._get_slaves():
                cfgfile.write("%s ansible_host=%s ansible_user=%s\n"
                              % (host[0], host[2], host[1]))

    def create_zk(self, file = 'zk.j2'):
        content = "zk://%s/mesos"
        ips = ["%s:2181" % host[2] for host in self._get_masters()]
        zk_string = ",".join(ips)
        with open(file, 'w') as zkfile:
            zkfile.write(content % zk_string)

inv = PacketInventory('<insert apikey here>', '<insert projectid here>')
inv.create_inventory()
inv.create_zk()
