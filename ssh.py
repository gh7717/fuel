#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import sys
import yaml

def ssh(host, com):
    command = 'ssh %s \'%s\'' % (host, com)
    output_of_command = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
    return output_of_command.stdout.readlines()


def main():
    ssh ('node-40', 'df -h')
    ssh ('node-40', 'lspci | grep Ethernet')
    ssh ('node-40', 'dmidecode -t system')
    ssh ('node-40', 'dmidecode -t bios')
    ssh ('node-40', 'hdparm -i /dev/vda')


if __name__ == "__main__":
    main()
