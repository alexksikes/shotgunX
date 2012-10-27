import sys, getopt, re

from lib.ensemble_selection import EnsembleSelection

def usage():
    print 'Usage: python shotgun.py [options] library_path train_name'
    print
    print 'Ensemble Selection as described by Rich Caruana et al.'
    print 'http://www.cs.cornell.edu/~caruana/caruana.icml04.revised.rev2.ps'
    print 'Implementation for document rankings.'
    print 
    print 'Coded by Alex Ksikes (ak469@cam.ac.uk).'
    print
    print 'Method: (default --sfr number of models)' 
    print '    --s                    ->     sort selection'
    print '    --b                    ->     backward elimination'
    print '    --f                    ->     forward selection'
    print '    --fr  num_iter         ->     forward selection with replacement'
    print '    --sfr num_iter         ->     sort then proceed with fr'
    print
    print 'Metrics: (default --NDCG@3)' 
    print '    --DCG@n                 ->     discounted cumulative gain at position n'
    print '    --NDCG@n                ->     normalized DCG at position n'
    print '    --NDCG@1+2+...+n        ->     NDCG at position 1 + 2 + ... + n'
    print
    print 'Options:'
    print '    --eval metrics         ->     evaluate the ensemble at each step on a list of metrics'
    print '    --o                    ->     also output the performance of each added model'
    print '    --no-cache             ->     turn caching off'
    print '    --make-ensemble file   ->     only make the ensemble at each iteration'
    print '    --verbose 0 1 2        ->     verbosity level (default 1)'
    print
    print 'Arguments:'
    print '    library_path           ->     path to the library of models'
    print '    train_name             ->     name of the directory to train shotgun on'

p_metric = re.compile('((?:--DCG@\d+)|(?:--NDCG@\d+)|(?:--NDCG@[+\d]))')
def parse_metrics(args):
    return [('--%s' % m, ) for m in p_metric.findall(args)]
    
def main():
    try:
        #opts, args = getopt.getopt(p.sub(args[1:], ''), '', 
        opts, args = getopt.getopt(sys.argv[1:], '', 
            ['s', 'f', 'b', 'fr=', 'sfr=', 'make-ensemble=', 'eval=', 'o', 'no-cache', 'help', 'verbose='])
        opts += parse_metrics(args[1:]) 
    except:
        usage(); sys.exit(2)
    
    method, metric, max_iter = 'sfr', 'NDCG@3', 0
    verbose_level, no_cache = 1, False
    models_file, eval_metrics, model_out = None, [], None 
    
    for o, a in opts:
        if o in ('--s', '--f', '--b'):
            method = o.replace('--', '')
        elif o in ('--fr', '--sfr'):
            method = o.replace('--', '')
            max_iter = int(a)
        elif o in ('--make-ensemble'):
            method = 'm'
            models_file = a
            no_cache = True
        elif o in ('--o'):
            model_out = True
        elif p_metric.match(o):
            metric = o.replace('--', '')
        elif o == '--verbose':
            verbose_level = int(a)
        elif o == '--eval':
            eval_metrics = a.split()
        elif o == '--no-cache':
            no_cache = True
        elif o in ('-h', '--help'):
            usage(); sys.exit()
    
    if len(args) < 1:
        usage()
    else:
        library_path, train_name = args
        es = EnsembleSelection(library_path, train_name, metric=metric, 
                verbose_level=verbose_level, no_cache=no_cache, 
                eval_metrics=eval_metrics, model_out=model_out)
        es.parse_model_library()
        es.run(method, max_iter, models_file)
    
if __name__ == "__main__":
    main()