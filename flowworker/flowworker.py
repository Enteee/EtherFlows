#! /usr/bin/env python2
# vim: set fenc=utf8 ts=4 sw=4 et :
#

import sys
import os
import shutil
import time
from threading import Thread
from Queue import Queue, Empty
from scapy.all import *

#MAC Addr of the flow generator 
FLOWGEN_MAC = "b4:be:b1:6b:00:b5"
#Timeout const in seconds
FLOW_TIMEOUT = 10

class Flow:
    def __init__(self, dst):
        self.pkts = []
        self.dst_hash = dst
        self.last_pkt = time.time()
    def write(self):
        if len(self.pkts) == 1:
            print("Only init pkt recived, flow with dst_hash: {} not written".format(self.dst_hash))
            return

        i = 0
        pktdump = PcapWriter(interface+"/"+self.dst_hash, append=True, sync=True)
        for pkt in self.pkts:
            pktdump.write(pkt)
            i += 1
        pktdump.close()
        print("Flow with dst_hash: {} written, included {} packets".format(self.dst_hash,i))


def packet_handler(pkt):
   #check for ether 
   if type(pkt) is Ether:
       #check dict
       dst = str(pkt.dst)
       if dst not in flows:
           sendp(Ether(dst=FLOWGEN_MAC, src=dst)/Raw("ENTE"),iface=interface,verbose=False)
           f = Flow(dst)
           flows[dst] = f
        

       flows[dst].pkts.append(pkt)
       flows[dst].last_pkt = time.time()

def flow_handler():
    to_remove = []
    i = 0;
    act_time = time.time()
    for dst in flows:
       #check timeout
       if act_time - flows[dst].last_pkt > FLOW_TIMEOUT:
           flows[dst].write()
           to_remove.append(dst)
       else:
           i += 1

    for dst in to_remove:
        del flows[dst]

    if i:
        print("Amount of active flows: {}".format(i))

def threaded_sniff_target(q):
  sniff(iface=interface, filter="ether src host {0}".format(FLOWGEN_MAC), store=0, prn = lambda x : q.put(x))

def threaded_sniff():
  q = Queue.Queue()
  sniffer = Thread(target = threaded_sniff_target, args = (q,))
  sniffer.daemon = True
  sniffer.start()
  while (True):
    try:
      pkt = q.get(timeout = 1)
      packet_handler(pkt)
    except Empty:
      #no new pkts so we have time to handle the flows
      flow_handler()
      pass


def print_usage():
    print("Usage: ./fworker interface")
    sys.exit(1)

if __name__ == "__main__":
    flows={}    
    dicto={}
    if len(sys.argv) != 2:
        print_usage()
    else:
        interface = str(sys.argv[1])


    if os.path.exists(interface):
        print("dir exists, clear dir")
        shutil.rmtree(interface)
    
    os.mkdir(interface)
    print("Start sniffing on Port "+interface)
    threaded_sniff()
