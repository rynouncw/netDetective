#!/usr/local/bin/python3.10 python3

#This program will attempt to detect where the issue is
#when a network connection is not made.  It will use traceroute 
#to get both the first hop IP address and to ensure that
#the full path is completed.

import pexpect
import re
import os
import socket
import sys
import netifaces

#get the local IP address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

local_ip=get_local_ip()

#get the default gateway
def get_default_gateway():
        gateways = netifaces.gateways()
        default_gateway = gateways['default'][netifaces.AF_INET][0]
        return default_gateway

default_gateway=get_default_gateway()


#talk to the user
print("Local IP Adress detected as "+local_ip)
print("Default Gateway detected as :"+default_gateway)
ipaddr = input("Please enter the ip address you wish to use for the destination:  (default is 8.8.8.8)")
if ipaddr =='':
        ipaddr="8.8.8.8"
trace_hops=input("Please enter the number of hops to test:  (default is 8)")
if trace_hops=="":
        trace_hops="8"
max_fail=input("Please enter the number of failures to allow:  (default is 3)")
if max_fail=='':
        max_fail=3
max_fail=int(max_fail)
print("Please stand by while I get the path to "+ipaddr)

#use traceroute to get the routing of the first 8 hops.  If we 
#complete 6 hops, we will assume that the internet connection to the ISP
# is functional.
child = pexpect.spawn('traceroute -m '+trace_hops+' '+ipaddr)

#store the output into a variable
output=''
while True:
        line = child.readline()
        if not line: 
              #sys.exit('Error:  Traceroute did not run.  Exiting the program now.')
              break
        line=str(line)
        output=output+line

# initializing the list object
wan_lst=[]

ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', output )
if ip:
        for i in ip:
                wan_lst.append(i)

#remove the destination addresses from the top of the list 
wan_lst.remove(ipaddr)
wan_lst.remove(ipaddr)

#displaying the extracted IP addresses
print(wan_lst)

#end Program
print('FIRST '+trace_hops+' hops found.  Starting ping monitoring.')

#begin pinging the host
child = pexpect.spawn('ping -c 65534 '+ipaddr)

counter=0
while counter < max_fail:
        line = child.readline()
        if not line: 
                break
        line=line.decode()
        line=line.rstrip("\n")
        print(line)
        #print(line+" | Number of Failures="+str(counter))
        if "unreachable" in line:
                counter+= 1              
        if "timeout" in line:
                counter+= 1
        if "unknown" in line:
                counter+= 1
        

#check each ip address in traceroute
for i in reversed(wan_lst):
        #print("TO IP ADDRESS "+i+" :")
        child = pexpect.spawn('ping -c 1 -t 1 '+i)
        while True:
                line = child.readline()
                if not line: 
                        break 
                line=line.decode()
                line=line.rstrip("\n")
                print(line)

#check local network
child = pexpect.spawn('ping -c 1 -t 1 '+default_gateway)
while True:
        line = child.readline()
        if not line: 
                break 
        line=line.decode()
        line=line.rstrip("\n")
        print(line)

#check local IP address
child = pexpect.spawn('ping -c 1 -t 1 '+local_ip)
while True:
        line = child.readline()
        if not line: 
                break 
        line=line.decode()
        line=line.rstrip("\n")
        print(line)

#check loopback address
child = pexpect.spawn('ping -c 1 -t 1 127.0.0.1')
while True:
        line = child.readline()
        if not line: 
                break 
        line=line.decode()
        line=line.rstrip("\n")
        print(line)       

print("PROBLEM DETECTED!  Please review screen output to determine where the issue is.")