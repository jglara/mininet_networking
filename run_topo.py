#!/usr/bin/python

"Networking Assignment 2"

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, output
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange, custom, quietRun, dumpNetConnections
from mininet.cli import CLI

from time import sleep, time
from multiprocessing import Process
from subprocess import Popen
import argparse

import sys
import os

from linuxrouter import NetworkTopo

parser = argparse.ArgumentParser(description="Topology bandwith and TCP tests")

parser.add_argument('--dir', '-d',
                    help="Directory to store outputs",
                    default="results")

parser.add_argument('--cli', '-c',
                    action='store_true',
                    help='Run CLI for topology debugging purposes')

parser.add_argument('--time', '-t',
                    dest="time",
                    type=int,
                    help="Duration of the experiment.",
                    default=60)

# Expt parameters
args = parser.parse_args()

if not os.path.exists(args.dir):
    os.makedirs(args.dir)

lg.setLogLevel('info')

def waitListening(client, server, port):
    "Wait until server is listening on port"
    if not 'telnet' in client.cmd('which telnet'):
        raise Exception('Could not find telnet')
    cmd = ('sh -c "echo A | telnet -e A %s %s"' %
           (server.IP(), port))
    while 'Connected' not in client.cmd(cmd):
        output('waiting for', server,
               'to listen on port', port, '\n')
        sleep(.5)

def progress(t):
       # Begin: Template code
    while t > 0:
        print '  %3d seconds left  \r' % (t)
        t -= 1
        sys.stdout.flush()
        sleep(1)

def start_tcpprobe():
    os.system("rmmod tcp_probe 1>/dev/null 2>&1; modprobe tcp_probe port=5001")
    Popen("cat /proc/net/tcpprobe > %s/tcp_probe.txt" % args.dir, shell=True)

def stop_tcpprobe():
    os.system("killall -9 cat; rmmod tcp_probe")



def run_topology_experiment(net):
    "Run experiment"

    seconds = args.time

    # Start the bandwidth in the background    
    net.getNodeByName('r0').cmd("sleep 1; bwm-ng -t %s -o csv -u bits -T rate -C ',' > %s/bw.txt &" % (1 * 1000, args.dir))

    start_tcpprobe()

    # Get receiver and clients
    recvr = net.getNodeByName('receiver')
    sender = net.getNodeByName('sender')


    # Start the receiver
    print "Starting iperf on the receiver"
    port = 5001
    recvr.cmd('iperf3 -s -p', port,
              '> %s/iperf_server.txt' % args.dir, '&')

    waitListening(sender, recvr, port)

    print "Starting iperf on the sender"
    sender.sendCmd('iperf3 -c %s -p %s -t %d -i 1 --json > %s/iperf_%s.txt' % (recvr.IP(), 5001, seconds, args.dir, recvr))

    # Turn off and turn on links
    print "waiting for the sender to finish"
    sender.waitOutput()

    print "Sender finished. Killing receiver"
    recvr.cmd('kill %iperf3')

    # Shut down monitors
    stop_tcpprobe()

def check_prereqs():
    "Check for necessary programs"
    prereqs = ['telnet', 'bwm-ng', 'iperf3', 'ping']
    for p in prereqs:
        if not quietRun('which ' + p):
            raise Exception((
                'Could not find %s - make sure that it is '
                'installed and in your $PATH') % p)

def main():
    "Create and run experiment"
    start = time()

    topo = NetworkTopo()

    host = custom(CPULimitedHost, cpu=.15)  # 15% of system bandwidth
#    link = custom(TCLink, max_queue_size=200)
#    net = Mininet(topo=topo, host=host, link=link )
    net = Mininet(topo=topo, host=host, controller=None )

    net.start()

    print "*** Dumping network connections:"
    dumpNetConnections(net)

    print "*** Testing connectivity"

    net.pingAll()

    if args.cli:
        # Run CLI instead of experiment
        CLI(net)
    else:
        print "*** Running experiment"
        run_topology_experiment(net)

    net.stop()
    end = time()
    os.system("killall -9 bwm-ng")
    print "Experiment took %.3f seconds" % (end - start)

if __name__ == '__main__':
    check_prereqs()
    main()
