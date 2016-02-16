import argparse
import matplotlib as m
import matplotlib.pyplot as plt
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--iface', dest="iface", default='eth0')
parser.add_argument('-f', '--file', dest="file", required=True)
parser.add_argument('-o', '--out', dest="out", default=None)

args = parser.parse_args()

"""
https://github.com/vgropp/bwm-ng/blob/master/README
csv output format: 
Type rate:
unix timestamp;iface_name;bytes_out/s;bytes_in/s;bytes_total/s;bytes_in;bytes_out;packets_out/s;packets_in/s;packets_total/s;packets_in;packets_out;errors_out/s;errors_in/s;errors_in;errors_out\n
Type svg, sum, max:
unix timestamp;iface_name;bytes_out;bytes_in;bytes_total;packets_out;packets_in;packets_total;errors_out;errors_in\n
Use --count 0 to skip the all zero output after start.
"""
def parse_file(f):
    times = defaultdict(list)
    bytes_in_s = defaultdict(list)
    bytes_out_s = defaultdict(list)
    errors_in_s = defaultdict(list)
    errors_out_s = defaultdict(list)
    for l in open(f).xreadlines():
        fields = l.strip().split(',')
        if len(fields) != 16:
            break
        iface = fields[1]
        times[iface].append( int(fields[0]) )
        bytes_out_s[iface].append( float( fields[2]))
        bytes_in_s[iface].append( float( fields[3]))
        errors_out_s[iface].append( float( fields[12]))
        errors_in_s[iface].append( float( fields[13]))


    return times, bytes_in_s, bytes_out_s, errors_in_s, errors_out_s

################################################################################
m.rc('figure', figsize=(16, 6))
fig = plt.figure()


times, bytes_in_s, bytes_out_s, errors_in_s, errors_out_s = parse_file(args.file)
t = times[args.iface]

# plot 1
bytes_in_Plot = fig.add_subplot(2, 2, 1)
bytes_in_Plot.plot(t, bytes_in_s[args.iface])
bytes_in_Plot.set_title("bytes_in/s")

# plot 2
bytes_out_Plot = fig.add_subplot(2, 2, 2)
bytes_out_Plot.plot(t, bytes_out_s[args.iface])
bytes_out_Plot.set_title("bytes_out/s")

# plot 3
errors_in_Plot = fig.add_subplot(2, 2, 3)
errors_in_Plot.plot(t, errors_in_s[args.iface])
errors_in_Plot.set_title("errors_in/s")

# plot 4
errors_out_Plot = fig.add_subplot(2, 2, 4)
errors_out_Plot.plot(t, errors_out_s[args.iface])
errors_out_Plot.set_title("errors_out/s")



if args.out:
    print 'saving to', args.out
    plt.savefig(args.out)
else:
    plt.show()
