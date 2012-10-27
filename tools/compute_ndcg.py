# Author: Alex Ksikes (alex.ksikes@gmail.com)

# TODO:
# - output to stdout a file with line nDCG1, nDCG3, nDCGn.
# - output to stdout a single number which is the averaged nDCG.
# - output DCG solely.

import sys, os

import model_library

def compute_ndcg(dir, out_dir, per_query=False, order_summary=True):
    models = model_library.read_dir(dir)
    
    sum_f = open(os.path.join(out_dir, 'summary.ndcg'), 'w')
    for model in models:
        if per_query:
            sys.stdout = open(os.path.join(out_dir, model.name + '.ndcg'), 'w')
            model.output_perf_by_query()
        else:
            model.compute_perf()
        
        print model
        sum_f.write('%s\t%s\n' % (model.name, model.get_perf()))
    
    if order_summary:
        sum_f = open(os.path.join(out_dir, 'summary.ndcg'), 'w')
        for model in sorted(models, reverse=True):
            sum_f.write('%s\t%s\n' % (model.name, model.get_perf()))
        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python compute_ndcg.py predictions_dir out_dir"
    else:
        compute_ndcg(sys.argv[1], sys.argv[2], per_query=True)