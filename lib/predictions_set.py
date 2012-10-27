'''
Author: Alex Ksikes (alex.ksikes@gmail.com)

shotgun.Model or perf.Metric take predictions which normally are numpy vectors.
In our setting an example is actually a set of predictions on which ndcg is computed.
'''

import re
from numpy import array, zeros

import perf

class Predictions:
    def __add__(self, predictions): pass
    
    def __sub__(self, predictions): pass
    
    def __mul__(self, predictions): pass

    def __div__(self, scalar): pass

class PredictionsSet(Predictions):
    def __init__(self, predictions):
        self.predictions = predictions
        
    def __add__(self, predictions): 
        return PredictionsSet([i + j for i, j in zip(self.predictions, predictions)])
        
    def __sub__(self, predictions):
        return PredictionsSet([i - j for i, j in zip(self.predictions, predictions)])
    
    def __mul__(self, scalar):
        return PredictionsSet([scalar * i for i in self.predictions])

    def __div__(self, scalar):
        return self * (1.0 / scalar)
        
    def __getitem__(self, item):
        return self.predictions[item]
    
    def __iter__(self):
        return self.predictions.__iter__()

    def __repr__(self):
        return '\n'.join([','.join(map(str, l)) for l in self])
    
    def __len__(self):
        return len(self.predictions)

#class TargetsSet(PredictionsSet):
#    def __init__(self, predictions, at=3):
#        self.predictions = predictions
#        if isinstance(at, list):
#            self.idcgs = self.compute_iDCGs_values(at)
#        else:
#            self.idcgs = self.compute_iDCG_values(at)
#        
#    def compute_iDCG_values(self, at):
#        return [perf.compute_DCG(t, t, at) for t in self.predictions]
#
#    def compute_iDCGs_values(self, at=[]):
#        return [perf.compute_DCGs(t, t, at) for t in self.predictions]

class TargetsSet(PredictionsSet):
    def __init__(self, predictions, at=3, ats=[]):
        self.predictions = predictions
        self.idcgs = self.compute_IDCG_values(at)
        
        if ats:
            self.idcgs_at = self.compute_IDCGs_values(ats)
        
    def compute_IDCG_values(self, at=3):
        return [perf.compute_DCG(t, t, at) for t in self.predictions]

    def compute_IDCGs_values(self, at=[]):
        return [perf.compute_DCGs(t, t, at) for t in self.predictions]

def read_predictions(f):
    return PredictionsSet([array(map(float, l.split(','))) for l in open(f)])  

def read_targets(f, metric='NDCG@3', eval_metrics=[]):
    if metric != 'NDCG@E':
        at = int(metric[-1])
        ats = [int(m[-1]) for m in eval_metrics if re.match('NDCG@\d$', m)]
    else:
        at = 3
        ats = [3]
    
    return TargetsSet([array(map(int, l.split(','))) for l in open(f)], at, ats)

def zero_predictions_set(size):
    return PredictionsSet(zeros(size))

