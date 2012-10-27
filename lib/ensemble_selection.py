'''
Author: Alex Ksikes (alex.ksikes@gmail.com)

Implementation of ensemble selection.
Link to the actual paper: http://www.cs.cornell.edu/~caruana/caruana.icml04.revised.rev2.ps
The algorithm should work for predictions or predictions sets.
'''

# TODO:
# - we are still binded to prediction sets: make_empty_ensemble, read_predictions, read_targets.
# >> should work with simpler predictions.
# - evaluate on many metrics.
# - does not work with smaller is better metric yet.
# - sort forward selection does not need to re-compute perf on sort.
# - we want to see the log live, flush stdout
# - evaluate and compute perf computes perf twice with NDCG

import copy, getopt, re

import model_library
from model import Model, FileModel, Ensemble, copy_ensemble

class EnsembleSelection:
    def __init__(self, library_path, train_name, metric, verbose_level=1, no_cache=False, eval_metrics=[], model_out=None):
        self.library_path = library_path          # path of the files contraining the models
        self.train_name = train_name              # name of dataset used to hill climbing
        self.metric = metric                      # metric used to hill climbing
        self.eval_metrics = eval_metrics          # metric used to evaluate the models
        self.v = verbose_level > 0                # show progress on stdout
        self.vv = verbose_level > 1               # also which model gets tried for addition
        
        self.library = []                         # holds the models used for hill climbing in memory
        self.library_files = {}                   # used for evaluation
        self.out = {}                             # writes the perf files test_name.perf
        self.es_test = {}                         # the ensembles on each test set
        self.es = None                            # the ensemble on the hill climbing set
        self.no_cache = no_cache                  # used to turn caching off
        self.model_out = model_out and {'':''}    # used to write the perfs of each model
        
    def add_model(self, model):
        for test, es in self.es_test.items():
            es.add(self.get_model_from_library(model, test))
            
#            if self.model_out:
#                m.evaluate(self.eval_metrics)
#                m.write_perfs(self.model_out[test])
            
        self.write_perf()
        
    def remove_model(self, model):
        for test, es in self.es_test.items():
            es.remove(self.get_model_from_library(model, test))
            
        self.write_perf()
        
    def add_models(self, models):
#        for model in models:
#            for test, es in self.es_test.items():
#                es.add(self.get_model_from_library(model, test), compute_perf=False)

        for test, es in self.es_test.items():
            for model in models:
                es.add(self.get_model_from_library(model, test))
                
        for test, es in self.es_test.items():
            es.name = '-'
            es.compute_perf()
        
        self.write_perf()
            
    def get_model_from_library(self, model, test):
        return self.library_files[test][model.name]
#        
#        if test != self.train_name or self.no_cache:
#            p = predictions.read_predictions(self.library_files[test][model.name])
#            t = self.es_test[test].targets
#            model = Model(p, t, name=model.name)
#        return model
        
    def get_ensemble_copy(self):
        return copy_ensemble(self.es)
    
    def write_perf(self):
        for test, es in self.es_test.items():
            es.compute(self.eval_metrics)
            es.write(self.out[test])
        
        if self.v: print self.es
        sys.stdout.flush()
        
#        for test, out in self.out.items():
#            if self.eval_metrics:
#                self.es_test[test].evaluate(self.eval_metrics)
#                self.es_test[test].write_perfs(out)
#            else:
#                out.write('%s\n' % self.es_test[test])
#            out.flush()
#        
#        if self.v: print self.es
#        sys.stdout.flush()
    
    def sort(self, max_iter=0, sort_init=True):
        if self.v: 
            print 'Performing sort ...'
        
        if sort_init:
            self.sort_model_library()
        
        for model in self.library[0:max_iter]:
            self.add_model(model)
            
    def forward_selection(self, max_iter, sort_init=True, replacement=True):
        if self.v: 
            print 'Performing forward selection ...'
        
        if sort_init:
            self.sort_model_library()

        def get_best_model():
            #p = [self.es.get_perf_with_model(m, verbose=self.vv) for m in self.library]
            p = [self.es.get_perf_with_model(m) for m in self.library]
            return self.library[pe.index(max(p))]
            
        for i in range(max_iter) or not self.library:
            model = get_best_model()
            self.add_model(model)
            if not replacement: 
                self.library.remove(model)
            
    def sort_forward_selection(self, max_iter, replacement=True):
        if self.v: 
            print 'Performing sort and then proceed with forward selection ...'
        
        def get_best_iteration():
            self.sort_model_library()
            es = self.get_ensemble_copy()
            p = [es.add_and_perf(m) for m in self.library]
            return p.index(max(p)) + 1
            
#            p = []
#            for model in self.library:
#                es.add(model)
#                p.append(es.get_perf())
#                if self.vv:
#                    print '%s with added model %s of perf %s' % \
#                        (es.get_perf(), model.get_pretty_name(), model.get_perf())
            
                    
        best_i = get_best_iteration()
        if self.v:
            print 'Best iteration for sort: %s' % best_i
        
        self.sort(best_i, sort_init=False)
        self.forward_selection(max_iter - best_i, sort_init=False, replacement=replacement)
            
    def backward_elimination(self):
        if self.v: 
            print 'Performing backward elimination ...'
        
        self.add_models(self.library)
        
        def get_best_model():
            p = [self.es.get_perf_without_model(m) for m in self.library]
            return self.library[pe.index(max(p))]
        
        while(self.library):
            model = get_best_model()
            self.library.remove(model)
            self.remove_model(model)
            
    def sort_model_library(self):
        if self.v: 
            print '=' * 80
            print 'Sort the model library ...'
        
        for model in self.library:
            model.compute_perf()
#            if self.v: 
#                print model

        self.library.sort(reverse=True)
        
        if self.v: 
            print 'The library is now sorted:'
            print '\n'.join(['%s\t%s' % (i, model) for i, model in enumerate(self.library)])
            
    def make_ensemble(self, models_file):
        def get_model(model_name):
            return [model for model in self.library if model.get_pretty_name() == model_name][0]
        
        for model_name in open(models_file, 'U'):
            self.add_model(get_model(model_name.strip()))

    def parse_model_library(self):
        if self.v: 
            print '=' * 80
            print 'Parsing model library ...'
        
        # parsing the model library
        (target_files, self.library_files) = model_library.parse(self.library_path)
        
        # making empty ensembles
        for test_name, path in self.target_files:
            if self.v: 
                print 'Reading target file: %s ...' % path
            target = predictions.read_targets(path, metric=self.metric)
            self.es_test[test_name] = model.empty_ensemble(target, self.metric)
            self.out[test_name] = open('%s.perf' % test, 'w')
#            if self.model_out: 
#                self.model_out[test] = open('%s.models.perf' % test, 'w')
        
        # caching models on train set
        for model_name, path in self.library_files[self.train_name].items():
            if self.no_cache:
                model = FileModel(path, target, name=model_name, metric=self.metric)                        
            else:
                if self.v: 
                    print 'Reading prediction file: %s ...' % model_path
                p = predictions.read_predictions(path)
                model = Model(p, target, name=model_name, metric=self.metric)
            self.library.append(model)
        
        # the ensemble to be optimized
        self.es = self.es_test[self.train_name]
        
    def run(self, method='sfr', max_iter=0, models_file=None):
        max_iter = max_iter or len(self.library)
        
        if self.v:
            print "=" * 80
            print 'Running Ensemble Selection ...'
            print 'Method: %s - Max iterations: %s' % (method, max_iter)
            print 'Hill climbing on metric: %s' % self.metric
            print 'Evaluating on metric(s): %s' % ' '.join(self.eval_metrics)
            
            print 'Hill climbing on dataset: %s (%s examples)' % \
                (self.library_files[self.train], len(self.es_test[self.train_name]))
            for t, f in self.library_files.items():
                if t != self.train_name:
                    print 'Testing on dataset: %s (%s examples)' % (f, len(self.es_test[t]))
            
            print 'Performance will be found in .perf files'
            print 'Performance of individual models will be found in .models.perf files'
        
        if method == 's':
            self.sort()        
        elif method == 'f':
            self.forward_selection(max_iter, replacement=False)
        elif method == 'fr':
            self.forward_selection(max_iter)
        elif method == 'b':
            self.backward_elimination()
        elif method == 'sfr':
            self.sort_forward_selection(max_iter)
        elif method == 'm':
            self.make_ensemble(models_file)
