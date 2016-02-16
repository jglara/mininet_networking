import argparse
import matplotlib as m
import matplotlib.pyplot as plt
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', dest="port", default='5001')
parser.add_argument('-f', '--file', dest="file", required=True)
parser.add_argument('-o', '--out', dest="out", default=None)

args = parser.parse_args()

"""
TCP PROBE Sample line (see http://lxr.free-electrons.com/source/net/ipv4/tcp_probe.c)
tstamp      src                 dst             len snd_nxt   snd_una   snd_wnd  rcv_wnd    snd_cwnd  ssthresh  srtt
9.308807919 192.168.1.100:59678 10.0.0.100:5001 32  0x83623c4 0x835dfe4 12       2147483647 34816     5         29696
"""
def parse_file(f):
    times = defaultdict(list)
    cwnd = defaultdict(list)
    srtt = defaultdict(list)
    ssthresh = defaultdict(list)
    swnd = defaultdict(list)
    rwnd = defaultdict(list)
    for l in open(f).xreadlines():
        fields = l.strip().split(' ')
        if len(fields) != 11:
            break
        dport = int(fields[2].split(':')[-1])
        times[dport].append( float(fields[0]) )
        swnd[dport].append( int(fields[6]) )
        rwnd[dport].append( int(fields[7]) )
        cwnd[dport].append( int(fields[8]) )
        ssthresh[dport].append( int(fields[9]) )
        srtt[dport].append( int(fields[10] ))
    return times, swnd, rwnd, cwnd, ssthresh, srtt

################################################################################
m.rc('figure', figsize=(16, 6))
fig = plt.figure()


times, swnd, rwnd, cwnds,ssthresh, srtt = parse_file(args.file)
t = times[int(args.port)]

# plot 1
cwndPlot = fig.add_subplot(3, 2, 1)
cwndPlot.plot(t, cwnds[int(args.port)])
cwndPlot.set_title("send_cwnd")

# plot 2
ssthreshPlot = fig.add_subplot(3, 2, 2)
ssthreshPlot.plot(t, ssthresh[int(args.port)])
ssthreshPlot.set_title("ssthresh")

# plot 3
srttPlot = fig.add_subplot(3, 2, 3)
srttPlot.plot(t, srtt[int(args.port)])
srttPlot.set_title("srtt")

# plot 4
swndPlot = fig.add_subplot(3, 2, 4)
swndPlot.plot(t, swnd[int(args.port)])
swndPlot.set_title("swnd")

# plot 5
rwndPlot = fig.add_subplot(3, 2, 5)
rwndPlot.plot(t, rwnd[int(args.port)])
rwndPlot.set_title("rwnd")


if args.out:
    print 'saving to', args.out
    plt.savefig(args.out)
else:
    plt.show()
