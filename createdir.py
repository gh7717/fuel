#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import sys
import yaml
import pycurl

def curlRequest(url):
    class ContentCallback:
         # This class has informations describe nodes. 
         def __init__(self):
            self.contents = ''
         def content_callback(self, buf):
            self.contents = self.contents + buf

    t = ContentCallback()
    try:
        # get information about nodes and write it in class ContentCallback
        info = pycurl.Curl()
        info.setopt(info.URL, url)
        info.setopt(info.WRITEFUNCTION, t.content_callback)
        info.perform()
        info.close()
    except ValueError:
        print "Error: %s - not found" %url
    #return the information about nodes
    return yaml.load(t.contents)

def getNodesInfo():
    #get information about nodes on this url
    nodes = curlRequest('http://127.0.0.1:8000/api/v1/nodes')
    nodes_info = []
    # get only fqdn node's name 
    for node in nodes:
        node_info = {}
        node_info['fqdn'] = node['fqdn']
        nodes_info.append(node_info)
    return nodes_info

def main():
    nodes =  getNodesInfo()
    for i in nodes:
        try:
            # create a directory
            # for example: /var/log/remote/node-1.domain.tld
            subprocess.Popen('mkdir /var/log/remote/%s' %i['fqdn'], shell = True)
        except:
            print "Error: can't create a directory %s" % i['fqdn']

if __name__ == "__main__":
    main()
