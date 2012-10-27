import perf
import predictions_set

class Model:
    def __init__(self, predictions, targets, metric='NDCG@3', name='', perf=0):
        self.predictions = predictions
        self.targets = targets
        self.metric = metric
        self.name = name
        self.perf = perf
        
        self.eval_metrics = []
        self.eval_perfs = []
        
    def __cmp__(self, model):
        return cmp(self.get_perf(), model.get_perf())

    def compute_perf(self):
        self.perf = perf.compute(self.metric, self.get_predictions(), self.targets)
        
    def evaluate(self, eval_metrics):
        self.eval_metrics = eval_metrics
        self.eval_perfs = perf.compute_many(self.eval_metrics, self.predictions, self.targets)
        
    def output_perf_by_query(self):
        self.perf = perf.compute(self.metric, self.predictions, self.targets, verbose=True)
    
    def get_perf(self):
        return self.perf
    
    def get_name(self):
        return self.name
    
    def get_pretty_name(self):
        return re.sub('(^.*?\.tsv.)|(\.ini)|(\.txt)|(\.predictions)', '', self.name)
    
    def get_predictions(self):
        return self.predictions
    
    def __repr__(self):
        return '%s\t%s\t%s' % (self.metric, self.get_perf(), self.get_pretty_name())
    
    def write(self, out):
        for m, p in zip(self.eval_metrics, self.eval_perfs):
            out.write('%s\t%s\t%s\n' % (m, p, self.get_pretty_name()))
    
class FileModel(Model):
    def __init__(self, predictions_file, targets, metric='nDCG@3', name='', perf=0, verbose=True):
        Model.__init__(self, 0, targets, metric, name)
        self.predicions_file = predictions_file
        self.verbose = verbose
    
    def get_predictions(self):
        if self.verbose:
            print '*** Reading predictions for %s' % self.get_pretty_name(),
        p = predictions.read_predictions(self.predicions_file)
        if self.verbose: 
            print '- READ ***'
        return p
        
class Ensemble(Model):
    def __init__(self, predictions, targets, metric='nDCG@3', name='', perf=0, num_models=0):
        Model.__init__(self, predictions, targets, metric, name)
        self.perf = perf
        self.name = name
        self.num_models = num_models
    
    def get_predictions(self):
        return self.predictions / self.num_models
    
    def add(self, model):#, compute_perf=True):
        self.name = model.name
        self.num_models +=1
        self.predictions = self.predictions + model.get_predictions()
#        if compute_perf: self.compute_perf()

    def remove(self, model):#, compute_perf=True):
        self.name = model.name
        self.num_models -=1
        self.predictions = self.predictions - model.get_predictions()
#        if compute_perf: self.compute_perf()

    def add_and_perf(self, model):
        self.add()
        return self.get_perf()
        
    def get_perf_with_model(self, model, verbose=False):
        p = perf.compute(self.metric, 
            (self.predictions + model.get_predictions()) / (self.num_models + 1), 
            self.targets)
        
        if verbose:
            print '%s with added model %s of perf %s' % (p, model.get_pretty_name(), model.get_perf())
        return p

    def get_perf_without_model(self, model, verbose=False):
        p = perf.compute(self.metric, 
            (self.predictions - model.get_predictions()) / (self.num_models - 1), 
            self.targets)
            
        if verbose:
            print '%s with removed model %s of perf %s' % (p, model.get_pretty_name(), model.get_perf())
        return p

    def __len__(self):
        return self.num_models
    
    def __repr__(self):
        return '%s\t%s\t%s\t%s' % (len(self), self.metric, self.get_perf(), self.get_pretty_name())

    def write(self, out):
        for m, p in zip(self.eval_metrics, self.eval_perfs):
            out.write('%s\t%s\t%s\t%s\n' % (len(self), m, p, self.get_pretty_name()))

def empty_ensemble(targets, metric='NDCG@3'):
    return Ensemble(predictions.zero_predictions_set(len(targets)), targets, metric)

def copy_ensemble(es):
    return Ensemble(copy.deepcopy(es.predictions), es.targets, es.metric, es.name, es.perf, es.num_models)
