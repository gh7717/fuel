#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import sys
import yaml
import pycurl

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

def getNodesInfo(id):
    nodes = curlRequest('http://127.0.0.1:8000/api/v1/nodes')
    nodes_info = []
    for node in nodes:
        node_info = {}
        node_info['fqdn'] = node['fqdn']
        node_info['ip'] = node['ip']
        node_info['roles'] = node['roles']
        nodes_info.append(node_info)
    return nodes_info

def getClusterInfo(id):

    #safe_dump - output without tag "!!python/unicode"
    #print yaml.safe_dump(curlRequest('http://127.0.0.1:8000/api/v1/clusters/'))

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
    cluster_attributes = attributes['editable']

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

def main():
    id = chooseCluster()
    print yaml.safe_dump(getClusterInfo(id), default_flow_style=False)

if __name__ == "__main__":
    main()
