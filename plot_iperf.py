import argparse
import matplotlib as m
import matplotlib.pyplot as plt
from collections import defaultdict

import json

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', dest="file", required=True)
parser.add_argument('-o', '--out', dest="out", default=None)


args = parser.parse_args()

def parse_file(f):
    bits_per_second = []
    retransmits= []
    snd_cwnd= []
    lines = open(f).readlines()
    iperf_data = json.loads("".join(lines[1:]))
    for interval in iperf_data["intervals"]:
        st=interval["streams"][0]
        bits_per_second.append(st["bits_per_second"])
        retransmits.append(st["retransmits"])
        snd_cwnd.append(st["snd_cwnd"])

    return bits_per_second,retransmits,snd_cwnd

m.rc('figure', figsize=(15, 10))
fig = plt.figure()


bits_per_second, retransmits, snd_cwnd = parse_file(args.file)


# plot 1
bits_plot = fig.add_subplot(3,1,1)
bits_plot.plot(bits_per_second)
bits_plot.set_title("bits per second/s")

# plot 2
retransmit_plot = fig.add_subplot(3,1,2)
retransmit_plot.plot(retransmits)
retransmit_plot.set_title("retransmits")

#plot 3
sndcwnd_plot = fig.add_subplot(3,1,3)
sndcwnd_plot.plot(snd_cwnd)
sndcwnd_plot.set_title("sndcwnd")


if args.out:
    print 'saving to', args.out
    plt.savefig(args.out)
else:
    plt.show()


                               
    
