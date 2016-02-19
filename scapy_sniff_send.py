#!/usr/bin/env python
import sys
from scapy.all import *
from optparse import OptionParser
from multiprocessing import Process

def action_on_dev_up(pkt):
    if IP in pkt:
        print "IP : %s -> %s" % (pkt[IP].src,pkt[IP].dst)
#        send(pkt[IP])
        for p in fragment(pkt[IP]):
            sendp(Ether()/p, iface='r0-eth2')

def action_on_dev_down(pkt):
    if IP in pkt:
        print "IP : %s -> %s" % (pkt[IP].src,pkt[IP].dst)
#        send(pkt[IP])
        for p in fragment(pkt[IP]):
            sendp(Ether()/p, iface='r0-eth1')

def sniff_up():
    sniff(iface='r0-eth1', filter ='src net 192.168.1.0/24', prn = action_on_dev_up)

def sniff_down():
    sniff(iface='r0-eth2', filter ='src net 10.0.0.0/24', prn = action_on_dev_down)


if __name__ == '__main__':

    sendp(Ether()/IP(dst="10.0.0.100",ttl=(1,4)), iface="r0-eth2")

    print "Sniffing dev-Up"
    p_up = Process(target=sniff_up)
    p_up.start()

    print "Sniffing dev-down"
    p_down = Process(target=sniff_down)
    p_down.start()

    raw_input('Press Enter key to stop sniffing')
    p_up.terminate()              
    p_down.terminate()

