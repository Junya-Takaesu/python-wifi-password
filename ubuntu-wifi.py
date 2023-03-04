#!/usr/bin/python3.8
import subprocess
import re

def execute_command(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = p.communicate()
    return output.decode()

def main():
    commands = list()
    command = "sudo nmcli device | grep -E '^.*wifi\s+connected' | awk -v network_interface=1 '{print $network_interface}'"
    network_interface = execute_command(command)
    command = f"sudo nmcli device wifi show-password ifname {network_interface}"
    wifi_password = execute_command(command)
    print(wifi_password)

if __name__=="__main__":
    main()