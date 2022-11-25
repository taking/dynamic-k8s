#!/usr/bin/env python3
import json, os, re, sys, time, shutil
import yaml
import argparse
from distutils.dir_util import copy_tree
from pathlib import Path
import subprocess
from ansinv import *

# # https://pypi.org/project/ansinv/
def generate(_count, _username, _password, _port, _ip, _reset):   
    
    ips_list_len = len(_ip)
    
    # Initialize empty inventory
    inventory = AnsibleInventory()

    # Create required groups
    for grp_name in "all", "kube_control_plane", "etcd", "kube_node", "calico_rr", "k8s_cluster":
        inventory.add_groups(AnsibleGroup(grp_name))

    for i in range(ips_list_len):
        host_name="cluster-" + str(i+1)
        if i<_count:
            etcd_name = "etcd" + str(i+1)
            print("[master]")
            print("  - host_name is ", host_name)
            print("  - host_ip is ", _ip[i])

            if i == 0:
                # [all]
                inventory.group("all").add_hosts(AnsibleHost(host_name, ansible_host=_ip[i], etcd_member_name=etcd_name))
                # [etcd]
                inventory.group("etcd").add_hosts(AnsibleHost(host_name))
            else:
                # [all]
                inventory.group("all").add_hosts(AnsibleHost(host_name, ansible_host=_ip[i]))
            # [kube_control_plane]
            inventory.group("kube_control_plane").add_hosts(AnsibleHost(host_name))
            # [kube_node]
            inventory.group("kube_node").add_hosts(AnsibleHost(host_name))
        else:
            print("[worker]")
            print("  - host_name is ", host_name)
            print("  - host_ip is ", _ip[i])
            # [all]
            inventory.group("all").add_hosts(AnsibleHost(host_name, ansible_host=_ip[i]))
            # [kube_node]
            inventory.group("kube_node").add_hosts(AnsibleHost(host_name))


    # _path_ssh=os.path.expanduser('~')+"/.ssh/gedge.pem"
    # print("#344 : ", _path_ssh)
    # [all:vars]
    inventory.group("all").groupvars.update(ansible_user=_username, ansible_ssh_pass=_password, ansible_sudo_pass=_password, ansible_port=_port, ansible_connection="ssh", ansible_ssh_timeout=30)

    inventory.group("calico_rr").add_hosts("")
    inventory.group("k8s_cluster").add_children(inventory.group("kube_control_plane"), inventory.group("kube_node"), inventory.group("calico_rr"))

    workerPath = Path(os.getcwd() + "/inventory/dynamic")
    print(workerPath)
    if workerPath.exists():
        shutil.rmtree(workerPath)
        copy_tree("./inventory/sample", "./inventory/dynamic")
        _path = os.getcwd()+"/inventory/dynamic/inventory.ini"
        with open(_path, "w") as file:
            file.write(str(inventory))
        print("Option Changing...")
        changeOption()
        print("Provising...")
        if _reset == 1:
            ansible(3)
        else:
            ansible(1)
            ansible(2)
    else:
        copy_tree("./inventory/sample", "./inventory/dynamic")
        _path = os.getcwd()+"/inventory/dynamic/inventory.ini"
        with open(_path, "w") as file:
            file.write(str(inventory))
        print("Option Changing...")
        changeOption()
        print("Provising...")
        if _reset == 1:
            ansible(3)
        else:
            ansible(1)
            ansible(2)
            

def ansible(_type):
    if _type == 1:
        cmd_reculsive = ['ctr', 'image', 'pull', 'quay.io/kubespray/kubespray:v2.19.0']
    elif _type == 2:
        cmd_reculsive = ['nerdctl', 'run', '--rm', '-it', '--name', 'provisioning', '-v', '/root/gedge-tta/inventory/dynamic:/inventory:rw,bind', 'quay.io/kubespray/kubespray:v2.19.0', '/inventory/start']
    elif _type == 3:
        print("######## reset ########")
        cmd_reculsive = ['nerdctl', 'run', '--rm', '-it', '--name', 'provisioning', '-v', '/root/gedge-tta/inventory/dynamic:/inventory:rw,bind', 'quay.io/kubespray/kubespray:v2.19.0', '/inventory/reset']
        
    p = subprocess.Popen(cmd_reculsive,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True)
                        
    while p.poll() == None:
        out = p.stdout.readline()
        print(out, end='')            
            
def changeOption():
    _path = os.getcwd() + "/inventory/dynamic/group_vars"
    _addons = _path + "/k8s_cluster/addons.yml"
    _k8sCluster = _path + "/k8s_cluster/k8s-cluster.yml"
    
    print(_addons)
    print(" - helm Enabled")
    subprocess.Popen(['sed', '-i', 's/helm_enabled: false/helm_enabled: true/', _addons], stdout=subprocess.PIPE)
    
    print(" - metrics_server Enabled")
    subprocess.Popen(['sed', '-i', 's/metrics_server_enabled: false/metrics_server_enabled: true/', _addons], stdout=subprocess.PIPE)
    
    print(_k8sCluster)
    print(" - kube_version v1.22.9 Changed")
    subprocess.Popen(['sed', '-i', 's/kube_version: v1.25.4/kube_version: v1.22.9/', _k8sCluster], stdout=subprocess.PIPE)
    subprocess.Popen(['sed', '-i', 's/kube_version: v1.23.7/kube_version: v1.22.9/', _k8sCluster], stdout=subprocess.PIPE)

# https://docs.python.org/ko/3.7/library/argparse.html
def main():
    # """Ansible Inventory를 생성해주는 간단한 프로그램입니다. (by taking)"""
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-c', '--count', type=int, default=1, help='Number of Control Plane. (Default. 1)')
    parser.add_argument('-u', '--username', type=str, help='ssh connection ID.')
    parser.add_argument('-p', '--password', type=str, help='ssh connection Password.')
    parser.add_argument('-P', '--port', type=str, help='ssh connection Port.')
    # parser.add_argument('-v', '--kubeversion', type=str, help='ssh connection Port.')
    parser.add_argument('-ip', '--ipaddress', type=str, nargs='*', help='ip address ex) 10.0.0.1 10.0.0.2 10.0.0.3")')
    parser.add_argument('--reset', type=int, help='reset ?')

    args = parser.parse_args()
    generate(args.count, args.username, args.password, args.port, args.ipaddress, args.reset)
  
if __name__ == '__main__':
    main()
