#!/usr/bin/env python

#:set tabstop=4 :set shiftwidth=4 :set smarttab :set explandtab
# -*- coding: utf-8 -*-
import subprocess
import yaml
import sys

class Cluster:
    """
        Cluster's describe:
        cluster ID
        cluster name
        type of deployment: HA or multinede
        network's type: Nova network, Neutrone
        segmentation: GRE or VLAN
        all backends
        nodes
    """
    id = 0
    name = None
    mode = None
    net_provider = None
    net_segment_type = None
    libvirt_type = None
    storages = {}
    nodes = {}
    def __parse(self, line): pass
    def __init__(self, id): pass
    def get_cluster_info(self): pass
    def get_node_info(self, env_id): pass

    def __parse(self, line):
        data = line.split('|')
        for i in xrange(0, len(data)):
            data[i] = ' '.join(data[i].split())
        return data

    def __init__(self, id):
       # get cluster's info
       get_cluster_data = 'sudo -u postgres -H -- psql -d nailgun -c \"select id, name, mode,net_provider, net_segment_type from clusters where id = %d;\"' % id
       cluster_data = subprocess.Popen(get_cluster_data, shell=True, stdout=subprocess.PIPE)

       cluster_data = cluster_data.stdout.readlines()
       
       # chose and parse line describe cluster
       cluster_info = self.__parse(cluster_data[2])
       # set informations about cluster
       try:
           self.id = int(cluster_info[0])
           self.name = cluster_info[1]
           self.mode = cluster_info[2]
           self.net_provider = cluster_info[3]
           self.net_segment_type = cluster_info[4]
       except:
           print "Environment ID not found"
           sys.exit(1)

        # get additional cluster's data
       get_cluster_data_additional = 'sudo -u postgres -H -- psql -d nailgun -c "select editable from attributes where cluster_id = %d;"' % id
       cluster_data = subprocess.Popen(get_cluster_data_additional, shell=True, stdout=subprocess.PIPE)
       cluster_data = cluster_data.stdout.readlines()
       # parse yaml 
       cluster_info =  yaml.safe_load(cluster_data[2])
       self.libvirt_type = cluster_info['common']['libvirt_type']['value']
       n = {}
       n['storages'] = {}
       for line in cluster_info['storage']:
           try:
               #self.storages[line] = cluster_info['storage'][line]['value']
                tmp = cluster_info['storage'][line]['value']
                n[line] = tmp
           except:
               self.storages[line] = cluster_info['storage'][line]
       self.storages = n.copy()
       print self.storages

    def get_cluster_info(self):
        nodes_info = self.get_node_info (self.id)
        cluster_info = {'ID':self.id, 'Name':self.name, 'Mode':self.mode, 'Network type':self.net_provider, 'Segmentation type':self.net_segment_type, 'nodes':self.nodes, 'storages':self.storages}
        return cluster_info


    def get_node_info(self, env_id):
        get_nodes_data = 'sudo -u postgres -H -- psql -d nailgun -c \"select nodes.fqdn,nodes.ip, roles.name, nodes.os_platform from nodes, roles, node_roles where node_roles.node = nodes.id and node_roles.role = roles.id and nodes.cluster_id = %d;\"' % env_id
        node_data = subprocess.Popen(get_nodes_data, shell=True, stdout=subprocess.PIPE)
        node_out = node_data.stdout.readlines()
        for i in xrange(2, len(node_out)-2):
            raw = self.__parse(node_out[i])
            if raw[0] not in self.nodes:
                self.nodes[raw[0]] = {}
            if 'ip' not in self.nodes[raw[0]]:
                self.nodes[raw[0]]['ip'] = raw[1]
            if 'OS' not in self.nodes[raw[0]]:
                self.nodes[raw[0]]['OS'] = raw[3]
            if 'roles' not in self.nodes[raw[0]]:
                self.nodes[raw[0]]['roles'] = []
            self.nodes[raw[0]]['roles'].append(raw[2])


def show_cluster_info():
    cluster_data = subprocess.call ('sudo -u postgres -H -- psql -d nailgun -c "select id, name, mode,net_provider, net_segment_type from clusters;"', shell=True)
    try:
        env_id = int(raw_input ('Enter environment ID for troubleshooting:'))
    except ValueError:
        print "Error in ID's enveronmenti: it is not number"
        sys.exit(1)
    except IOError:
        print "Input error"
        sys.exit(1)
    return env_id

def main():
    cluster = Cluster(show_cluster_info())
    # save information in the file. 
    # file is saved in directory where script is. 
    try:
        yaml_cluster = open('cluster_info.yaml', 'w')
        yaml_cluster.write(yaml.dump(cluster.get_cluster_info()))
        yaml_cluster.close()
    except IOError:
        print "Input/output error"
        sys.exit(1)
    print yaml.dump(cluster.get_cluster_info())
 

if __name__ == "__main__":
	main()
