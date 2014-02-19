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
            nodes[node['name']]['management_ip'] = node['internal_address']
            nodes[node['name']]['roles'].append(node['role'])
        except:
            nodes[node['name']] = {'management_ip':node['internal_address'], 'roles':[node['role']]}
    print nodes
def main():
    info = get_info_cluster()
    get_info_node(info)

if __name__ == "__main__":
        main()

