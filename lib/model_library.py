# Author: Alex Ksikes (alex.ksikes@gmail.com)

# TODO:
# - get_number_of_queries breaks if there is only one last query.
# - holes should be empty and zero (more compact).

import sys, os, random, re

import model
import predictions_set

fields = ['m:QueryId', 'm:DocId', 'm:Rating']
def get_score_from_dataset(dataset):
    for i, l in enumerate(open(dataset)):
        columns = l.split('\t')
        if i == 0:
            indexes = [columns.index(f) for f in fields]
        
        print '\t'.join([columns[i] for i in indexes])

def get_number_of_queries(dataset):
    f = open(dataset, 'rU'); f.readline()
    
    queries = {}
    no_queries = []
    for i, l in enumerate(f):
        query = l.split('\t')[0]
        
        if i == 0: 
            query_p = query
        
        if queries.has_key(query):
            queries[query] +=1
        else:
            queries[query] = 1
        
        if query != query_p:
            no_queries.append(queries[query_p])
            query_p = query
            
    no_queries.append(queries[query])
    return no_queries

def get_scores_histogramme(dataset):
    f = open(dataset, 'rU'); f.readline()
    
    scores = {}
    for l in f:
        sc = l.split('\t')[2].replace('\n', '')
        if scores.has_key(sc):
            scores[sc] +=1
        else:
            scores[sc] = 1
    for sc, n in sorted(scores.items()):
        print sc, n
    
score = dict(Detrimental=0, Bad=0, Fair=3, Good=7, Excellent=15, Perfect=31, **{'': 0})
def get_score(sc):
    return score[sc.replace('\r\n', '').strip()]

def extract_targets(dataset, no_queries=[]):
    f = open(dataset, 'rU'); f.readline()
    
    no_queries = no_queries or get_number_of_queries(dataset)
    for n in no_queries:
        lines = [f.readline() for i in range(n)]
        print ','.join([str(get_score(l.split('\t')[2])) for l in lines])
                    
def extract_predictions(predictions, dataset, no_queries=[]):
    f = open(predictions, 'rU')
    
    no_queries = no_queries or get_number_of_queries(dataset)
    for n in no_queries:
        print ','.join([f.readline().strip() for i in range(n)])

def get_file_out(out_dir, f, ext, remove=True):
    filename = '%s.%s' % (os.path.basename(f), ext)
    
    if remove:
        filename = re.sub('(^.*?\.tsv.)|(\.ini)|(\.txt)', '', filename)
    
    return open(os.path.join(out_dir, filename), 'w')
    
def build_model_library(doc_ranking_dir, dataset, out_dir):
    no_queries = get_number_of_queries(dataset)
    
    sys.stdout = get_file_out(out_dir, dataset, 'targets')
    extract_targets(dataset, no_queries)
    
    for f in os.listdir(doc_ranking_dir):
        sys.stdout = get_file_out(out_dir, f, 'predictions')
        extract_predictions(os.path.join(doc_ranking_dir, f), dataset, no_queries)
    
    sys.stdout.close()

def get_simplified_dataset(dataset):
    get_score_from_dataset(dataset)

def make_splits_fixed(testset_dir, splits, split_names):
    splits, split_names = map(int, splits.split(',')), split_names.split(',')
    splits = zip(splits, splits[1:])
    
    for f in os.listdir(testset_dir):
        lines = open(os.path.join(testset_dir, f), 'U').readlines()
        for split, split_name in zip(splits, split_names):
            open(os.path.join(split_name, f), 'w').write(''.join(lines[split[0]:split[1]]))

def make_splits(dir, split_percent, split_names, out_dir):
    for n in split_names:
        try: 
            os.makedirs(os.path.join(out_dir, n))
        except: 
            pass
    
    distrib = []
    for n, p in zip(split_names, split_percent):
        distrib.extend([n] * p)
    
    splits = {}
    for i, l in enumerate(open(os.path.join(dir, os.listdir(dir)[0]), 'U')):
        splits[i] = random.choice(distrib)
    
    for i, m in enumerate(os.listdir(dir)):
        print '%s writing %s ...' % (i, m)
        
        out = {}
        for n in split_names:
            out[n] = open(os.path.join(
                os.path.join(out_dir, n), m), 'w')
        
        for i, l in enumerate(open(os.path.join(dir, m), 'U')):
            out[splits[i]].write(l)
        
def parse(library_path):
    targets, models = {}, {}
    for r, d, filenames in os.walk(library_path):
        d = os.path.basename(r)
        
        if d not in models: models[d] = {}
        
        for f in filenames:
            f_path = os.path.join(r, f)
            
            ext = os.path.splitext(f)[-1]
            
            if ext == '.targets':
                targets[d] = f_path
            elif ext == '.predictions':
                models[d][f] = f_path
    
    return targets, models

def read_dir(dir):
    tf, mf = parse(dir)
    tf, mf = tf.values()[0], mf.values()[0]
    
    print 'Reading target file: %s ...' % tf
    t = predictions_set.read_targets(tf)
    
    models = []
    for m in mf:
        m = os.path.join(dir, m)
        print 'Reading prediction file: %s ...' % m
        
        p = predictions_set.read_predictions(m)
        models.append(model.Model(p, t, name=os.path.basename(m)))
    
    return models
