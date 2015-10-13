#! /usr/bin/env python2
# vim: set fenc=utf8 ts=4 sw=4 et :
#

import sys
import os
import shutil
import time
import signal
import struct
from threading import Thread
from Queue import Queue, Empty
from scapy.all import *

#MAC Addr of the flow generator 
FLOWGEN_MAC = "b4:be:b1:6b:00:b5"
#Timeout const in seconds
FLOW_TIMEOUT = 10
MAX_PKT = 100
running = True

class PcapPacket:
    def __init__(self, payload):
        self.caplen = len(payload)
        self.wirelen = self.caplen
        t = time.time()
        it = int(t)
        self.sec = it
        self.usec = int(round((t-it)*1000000))
        self.payload = payload
    def write(self):
        sys.stdout.write(struct.pack("IIII",self.sec, self.usec, self.caplen, self.wirelen))
        sys.stdout.write(str(self.payload))
        sys.stdout.flush()

def packet_handler(pkt):
   #check for ether 
   if type(pkt) is Ether:
       #check dict
       pcap = PcapPacket(pkt)
       dst = str(pkt.dst)
       src = str(pkt.src)
       if dst not in flows:
           sendp(Ether(dst=src, src=dst)/Raw("ENTE"),iface=interface,verbose=False)
           flows[dst] = True
       pcap.write()

def print_usage():
    print("Usage: ./fworker interface")
    sys.exit(1)

if __name__ == "__main__":
    flows={}    
    if len(sys.argv) != 2:
        print_usage()
    else:
        interface = str(sys.argv[1])

    #global pcap hdr
    hdr = struct.pack("IHHIIII", 0xa1b2c3d4L, 2, 4, 0, 0, MTU, 1)
    sys.stdout.write(hdr)
    sys.stdout.flush()

    sniff(iface=interface, filter="ether src host {0}".format(FLOWGEN_MAC), prn = packet_handler)

