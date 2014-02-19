#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess 
import  sys
import yaml


def download_yaml():
    try:
        admin_VIP = sys.argv[1]
    except NameError:
        print "Could you please enter primary controller IP\n ./troubleshooting.py <IP>"
        sys.exit()
    except IndexError:
        print "Could you please enter primary controller IP\n ./troubleshooting.py <IP>"
        sys.exit()

    scp_command = "scp %s:/etc/astute.yaml /root/" % admin_VIP
    scp = subprocess.Popen(scp_command, shell=True, stdout = subprocess.PIPE)

def get_info_cluster():
    download_yaml()
    try:
        yaml_file = open('/root/astute.yaml', 'r')
        data_cluster = yaml.safe_load(yaml_file)
        yaml_file.close()
    except IOError:
        print "Input/output error"
        sys.exit()
    return data_cluster

def get_info_node(cluster):
    nodes = {}
    for node in cluster['nodes']:
        #print node['name'],' - ' , node['role']
        try:
            nodes[node['fqdn']]['ip'] = ""
            nodes[node['fqdn']]['roles'].append(node['role'])
            nodes[node['fqdn']]['name'] = node['name']
        except:
            nodes[node['fqdn']] = {'management_ip':node['internal_address'], 'roles':[node['role']]}
    try:
        dnsmasq = open('/etc/dnsmasq.conf', 'r')
        for line in dnsmasq.readlines():
            info = line.split(',')
            if len(info) == 4:
                if info[2] in nodes:
                    nodes[info[2]]['ip'] = ' '.join(info[3].split())
    except IOError:
        print "Input/Output errors"
    return nodes

def main():
    info = get_info_cluster()
    print get_info_node(info)

if __name__ == "__main__":
        main()

