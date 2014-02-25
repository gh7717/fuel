#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import sys
import yaml
import pycurl
import ssh
import os

def curlRequest(url):
    class ContentCallback:
         def __init__(self):
            self.contents = ''
         def content_callback(self, buf):
            self.contents = self.contents + buf

    t = ContentCallback()
    try:
        info = pycurl.Curl()
        info.setopt(info.URL, url)
        info.setopt(info.WRITEFUNCTION, t.content_callback)
        info.perform()
        info.close()
    except ValueError:
        print "Error: %s - not found" %url
    return yaml.load(t.contents)

def parse(info):
    info_out = []
    for i in info:
         info_out.append((' '.join(i.split())).split(' '))
    return info_out

def getNodesInfo(id):
    nodes = curlRequest('http://127.0.0.1:8000/api/v1/nodes')
    nodes_info = []
    for node in nodes:
        if not(node['cluster'] is  None) and (int(node['cluster']) == id):
            node_info = {}
            node_info['fqdn'] = node['fqdn']
            node_info['ip'] = node['ip']
            node_info['roles'] = node['roles']
            node_info['network_data'] = node['network_data']
            node_info['disk'] = {}
            for disk in node['meta']['disks']:
                 node_info['disk'][disk['name']] = str(float(disk['size']) / (1024*1024*1024))+'G'
            tmp =  parse(ssh.ssh(node_info['fqdn'], 'df -h'))
            for i in xrange(1, len(tmp)):
                if len(tmp[i]) == 6:
                    node_info['disk'][tmp[i][-1]] = tmp[i][3]
                elif len(tmp[i]) == 5: # glance-image - bug (????)
                    node_info['disk'][tmp[i][-1]] = tmp[i][2]
            nodes_info.append(node_info)
    return nodes_info

def getClusterInfo(id):

    clusters = curlRequest('http://127.0.0.1:8000/api/v1/clusters/')
    cluster_info = {}

    for cluster in clusters:
        if int (cluster['id']) != id:
            continue
        else:
            try:
                cluster_info['release'] = {}
                cluster_info['id'] = cluster['id']
                cluster_info['mode'] = cluster['mode']
                cluster_info['name'] = cluster['name']
                cluster_info['net_provider'] = cluster['net_provider']
                cluster_info['net_segment_type'] = cluster['net_segment_type']
                cluster_info['release']['id'] = cluster['release']['id']
                cluster_info['release']['name'] = cluster['release']['name']
                cluster_info['attributes'] = {}
            except:
                print "Cluster ID error"
                sys.exit (1)
    attributes = curlRequest('http://127.0.0.1:8000/api/v1/clusters/%d/attributes/' % id)
    try:
        cluster_attributes = attributes['editable']
    except:
        print "Incorect cluster date"
        sys.exit(1)

    cluster_info['libvirt_type'] = cluster_attributes['common']['libvirt_type']['value']
    for line in cluster_attributes['storage']:
        try:
             cluster_info['attributes'][line] = cluster_attributes['storage'][line]['value']
        except:
             cluster_info['attributes'][line] = cluster_attributes['storage'][line]
    
    cluster_info['nodes'] = getNodesInfo(id)

    return cluster_info

def chooseCluster():
    clusters = curlRequest('http://127.0.0.1:8000/api/v1/clusters/')
    print "You have get %d clusters:" % len(clusters)
    print "ID\t| name \t| mode \t| network type \t"
    for i in clusters:
        print i['id'], "\t",  i['name'], "\t", i['mode'], "\t", i['net_provider']

    try:
        env_id = int(raw_input("Enter environment ID: "))
        return env_id
    except ValueError:
        print "ID is not number"
        sys.exit(1)

def saveClusterInfo(cluster):
    if not os.path.isdir('cluster'):
        os.mkdir('cluster')
    try:
        f = open('./cluster/cluster.yaml', 'w')
        f.write(yaml.safe_dump(cluster, default_flow_style=False))
        f.close()
        os.mkdir
    except IOError:
        print "Input/output error"
        sys.exit(1)
    for node in cluster['nodes']:
        if not os.path.isdir('./cluster/%s'%node['fqdn']):
            os.mkdir('./cluster/%s'%node['fqdn'])
        try:
            f = open('./cluster/%s/hardware.out'%node['fqdn'], 'w')
            f.write('dmidecode -t system\n')
            #f.write(str(ssh.ssh(node['fqdn'], 'dmidecode -t system')))
            tmp = ssh.ssh(node['fqdn'], 'dmidecode -t system')
            for i in tmp:
                f.write(' '.join(i.split()))
                f.write('\n')
            f.write('dmidecode -t bios\n')
            #f.write(str(ssh.ssh(node['fqdn'], 'dmidecode -t bios')))
            tmp = ssh.ssh(node['fqdn'], 'dmidecode -t bios')
            for i in tmp:
                f.write(' '.join(i.split()))
                f.write('\n')
            f.write('lspci\n')
            #f.write(str(ssh.ssh(node['fqdn'], 'lscpi')))
            tmp = ssh.ssh(node['fqdn'], 'lspci')
            for i in tmp:
                f.write(' '.join(i.split()))
                f.write('\n')
            
        except IOError:
            print "Input/output error"
            sys.exit(1)


def getServiceInfo(cluster):
    pass

def main():
    id = chooseCluster()
    cluster = getClusterInfo(id)
    saveClusterInfo(cluster)

if __name__ == "__main__":
    main()
