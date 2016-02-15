#!/usr/bin/python

"""
linuxrouter.py: Example network with Linux IP router

This example converts a Node into a router using IP forwarding
already built into Linux.

The topology contains a router with IP subnets:
 - 192.168.1.0/24 (interface IP: 192.168.1.1)
 - 10.0.0.0/8 (interface IP: 10.0.0.1)

 It also contains hosts, one in each subnet:
 - sender (IP: 192.168.1.100)
 - receiver (IP: 10.0.0.100)

 Routing entries can be added to the routing tables of the
 hosts or router using the "ip route add" or "route add" command.
 See the man pages for more details.

"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

from mininet.link import TCLink
from mininet.link import Link
from mininet.link import TCIntf
from mininet.node import CPULimitedHost

class MyTCLink( Link ):
    "Link with symmetric TC interfaces configured via opts"
    def __init__( self, node1, node2, port1=None, port2=None,
                  intfName1=None, intfName2=None,
                  addr1=None, addr2=None, ip1=None, ip2=None, **params ):
        Link.__init__( self, node1, node2, port1=port1, port2=port2,
                       intfName1=intfName1, intfName2=intfName2,
                       cls1=TCIntf,
                       cls2=TCIntf,
                       addr1=addr1, addr2=addr2,
                       params1=params,
                       params2=params )
        if ip1 is not None:
            self.intf1.setIP(ip1)

        if ip2 is not None:
            self.intf2.setIP(ip2)


class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):
    "A simple topology of a router with three subnets (one host in each)."

    def build( self, **_opts ):
        router = self.addNode( 'r0', cls=LinuxRouter, ip='192.168.1.1/24' )
        sender = self.addHost( 'sender', ip='192.168.1.100/24',
                           defaultRoute='via 192.168.1.1' )
        receiver = self.addHost( 'receiver', ip='10.0.0.100/8',
                           defaultRoute='via 10.0.0.1' )

        linkConfig = {'bw': 50, 'delay': '10ms', 'loss': 0, 'jitter': 0,
                   'max_queue_size': 1000 }

        self.addLink( sender, router, cls=MyTCLink, intfName2='r0-eth1', ip2='192.168.1.1/24')
        self.addLink( receiver, router, cls=MyTCLink, intfName2='r0-eth3', ip2='10.0.0.1/8', **linkConfig)

def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo, controller=None )  # no controller needed
    net.start()
    info( '*** Routing Table on Router\n' )
    print net[ 'r0' ].cmd( 'route' )
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
