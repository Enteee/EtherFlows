#! /usr/bin/env python2
# vim: set fenc=utf8 ts=4 sw=4 et :
#

import sys
import os
import shutil
from scapy.all import *

def packet_hanlder(pkt):
   #check for ether 
   if type(pkt) is Ether:
       #check dict
       dst = str(pkt.dst)
       if dst not in dicto:
           sendp(Ether(dst="b4:be:b1:6b:00:b5", src=dst)/Raw("ENTE"),iface=interface,verbose=False)
           dicto[dst] = 0
        

       dicto[dst] += 1
       
       pktdump = PcapWriter(interface+"/"+dst, append=True, sync=True)
       pktdump.write(pkt)
       pktdump.close()

def print_usage():
    print("Usage: ./fworker interface")
    sys.exit(1)

if __name__ == "__main__":
    
    dicto={}
    if len(sys.argv) != 2:
        print_usage()
    else:
        interface = str(sys.argv[1])


    if os.path.exists(interface):
        print("dir exists, clear dir")
        shutil.rmtree(interface)
    
    os.mkdir(interface)
    sniff(iface=interface, prn=packet_hanlder, filter="ether src host b4:be:b1:6b:00:b5", store=0)
