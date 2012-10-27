# Author: Alex Ksikes (alex.ksikes@gmail.com)

# To be run under windows (not under cygwin)

import sys, os, getopt, glob
from pylab import *
from numpy import *

def run(perf_files, labels=[], _title='', _range=(), legend_loc='lower right', auto_labels=False):
    if not labels:
        labels = [os.path.basename(f) for f in perf_files]
        if auto_labels:
            labels = [f for f in perf_files]
    
    if not _range:
        start, end = 0, 10000
    else:
        start, end = _range
    
    xlabel('Number of Models in the Ensemble')
    ylabel('NDCG@3')
    title(_title)
    
    for f, label, style in zip(perf_files, labels, get_linestyles()):
        d = mlab.load(f, usecols=[0,2])
        
        x = d[start:end,0]
        y = d[start:end,1]
        
        plot(x, y, style, label=label)
    
    grid(True)
    legend(loc=legend_loc)
    show()

def run2(perf_files, labels=[], _title='', _range=(), legend_loc='lower right', auto_labels=False):
    if not labels:
        labels = [os.path.basename(f) for f in perf_files]
        if auto_labels:
            labels = [f for f in perf_files]
    
    if not _range:
        start, end = 0, 10000
    else:
        start, end = _range
    
    #xlabel('Number of Models in the Ensemble')
    #ylabel('NDCG@n')
    
    xlabel('Models')
    ylabel('NDCG@3')
    
    title(_title)
    
    for f, label, c in zip(perf_files, labels, ('b', 'r')):
        #for ndcg_value, style in zip('NDCG@1 NDCG@2 NDCG@3 NDCG@4 NDCG@5'.split(), get_linestyles()):
        for ndcg_value, style2 in zip('NDCG@3'.split(), get_linestyles()):
            d = parse_perf_file(f, grep=ndcg_value, usecols=[1])
            l = '%s/%s' % (label, ndcg_value)
            
            #x = d[start:end,0]
            #y = d[start:end,1]
            y = d[start:end,0]
            x = array(range(len(y)))
            
            bar(x, y, color=c, label=l)
            #plot(x, y, style, label=l)
    
    grid(True)
    legend(loc=legend_loc)
    show()

def parse_perf_file(f, usecols=[0, 2], grep=''):
    data = []
    for l in open(f):
        if grep not in l:
            continue
        data.append([float(c) for i, c in enumerate(l.split('\t')) if i in usecols])
    return array(data)

def get_linestyles():
    colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
    markers = [m for m in Line2D.markers if isinstance(m, str) and len(m) == 1 and m != ' ']
    markers = markers[3:]
    return [c+m+'-' for c, m in zip(colors, markers)]

def usage():
    print 'Usage: python plot_perf.py [options] perf_files'
    print
    print '-t, --title         ->     plot title'
    print '-l, --labels        ->     label of each plot'
    print '-n                  ->     automatic labelling of the plots directory/file'
    print '-r, --range         ->     plot range (default 0:)'
    print '--legend-loc        ->     legend place (default "lower right")'
    
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 't:l:r:n',
            ['title=', 'labels=', 'range=', 'legend-loc=', 'help'])
    except getopt.GetoptError:
        usage(); sys.exit(2)
    
    title, labels, range, legend_loc = '', [], (), 'lower right'
    auto_labels = False
    
    for o, a in opts:
        if o in ('-t', '--title'):
            title = a
        elif o in ('-l', '--labels'):
            labels = a.split()
        elif o in ('-r', '--range'):
            range = map(int, a.split(':'))
        elif o in ('-n'):
            auto_labels = True
        elif o in ('--legend-loc'):
            legend_loc = a
        elif o in ('-h', '--help'):
            usage(); sys.exit()
    
    if len(args) < 1:
        usage()
    else:
        a = []
        for arg in args: a.extend(glob.glob(arg))
        run(a, _title=title, labels=labels, _range=range, 
            legend_loc=legend_loc, auto_labels=auto_labels)

if __name__ == "__main__":
    main()