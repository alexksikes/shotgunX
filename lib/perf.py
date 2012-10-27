# Author: Alex Ksikes (alex.ksikes@gmail.com)

# In order to have the same results as the production :
# - holes are handled as zeroes
# - in case of a tie the document with the lowest judgement wins
# - CG are discounted by log(2) / log(2 + i)

from numpy import *
import math, re

def compute(metric, predictions, targets, verbose=False):
    if metric == 'ACC': 
        return ACC(predictions, targets).compute()
    elif metric == 'RMSE': 
        return RMSE(predictions, targets).compute()
    elif metric == 'ROC': 
        return ROC(predictions, targets).compute()
    elif metric == 'SAR': 
        return SAR(predictions, targets).compute()
    elif re.match('DCG@\d$', metric):
        return DCG(predictions, targets, ).compute(int(metric[-1]))
    elif re.match('NDCG@\d$', metric):
        return NDCG(predictions, targets, verbose).compute(int(metric[-1]))
    elif metric == 'NDCG@E': 
        ndcg1, ndcg3 = compute_many(['NDCG@1', 'NDCG@3'], predictions, targets)
        return (ndcg1 + ndcg3) / 2
        
def compute_many(metrics, predictions, targets):
    at = [int(m[-1]) for m in metrics if re.match('NDCG@\d$', m)]
    return NDCG(predictions, targets).compute_many(at)
    
class Metric:
    name = ''
    def __init__(self, predictions, targets):
        self.predictions = predictions
        self.targets = targets
        self.a, self.b = 0, 0
        self.c, self.d = 0, 0
    
    def compute_cost_matrix(self):
        if is_cost_matrix_computed: return
        
    def is_cost_matrix_computed(self):
        return self.a and self.b and self.c and self.d
    
    def compute(self):
        pass

class ACC(Metric):
    def compute(self):
        self.compute_cost_matrix()

class RMSE(Metric):
    def compute(self):
        self.compute_cost_matrix()

class SAR(Metric):
    def compute(self):
        self.compute_cost_matrix()
        return Accuracy(self.predictions, self.targets).compute() + \
               RMSE(self.predictions, self.targets).compute() + 1 - \
               ROC(self.predictions, self.targets).compute()

class NDCG(Metric):
    def __init__(self, predictions, targets, verbose=False):
        self.predictions = predictions 
        self.targets = targets
        self.verbose = verbose
        
    def compute(self, at=3):
        ave_ndcg = 0
        for p, t, idcg in zip(self.predictions, self.targets, self.targets.idcgs):
            (dcg, docs)  = compute_DCG(p, t, at, return_docs=True)
            
            if idcg == 0:
                ndcg = 0
            else:
                ndcg = dcg / idcg
            
            if self.verbose:
                print '%s\t%s\t%s' % (ndcg, ','.join(docs), ','.join(map(str, sorted(t, reverse=True))[0:10]))
            
            ave_ndcg += ndcg
        return ave_ndcg / len(self.predictions)

    def compute_many(self, at=[1,2,3,4,5]):
        ave_ndcgs = {}
        for p, t, idcgs in zip(self.predictions, self.targets, self.targets.idcgs_at):
            dcgs = compute_DCGs(p, t, at)
            d = compute_DCG(p, t)
            
            for _at in at:
                if len(dcgs) < _at + 1:
                    dcg, idcg = dcgs[-1], idcgs[-1]
                else:
                    dcg, idcg = dcgs[_at], idcgs[_at]
                
                if idcg == 0:
                    ndcg = 0
                else:
                    ndcg = dcg / idcg
                
                if _at not in ave_ndcgs:
                    ave_ndcgs[_at] = 0
                
                ave_ndcgs[_at] += ndcg 
         
        return [ave_ndcgs[_at] / len(self.predictions) for _at in at]

def compute_DCG(prediction_set, target_set, at=3, return_docs=False):
    docs = sorted(zip(prediction_set, target_set), 
        reverse=True, key=lambda x: (x[0], -x[1]))[0:at]
        
    labels = []
    dcg = 0.0
    for i, (p, t) in enumerate(docs):
        dcg += t * math.log(2)/math.log(2+i)
        labels.append(str(t))
    
    if return_docs:
        return dcg, labels
    
    return dcg

def compute_DCGs(prediction_set, target_set, at=[1,2,3,4,5]):
    max_at = max(at)
    docs = sorted(zip(prediction_set, target_set), 
        reverse=True, key=lambda x: (x[0], -x[1]))[0:max_at]
    
    dcgs = [0.0]
    for i, (p, t) in enumerate(docs):
        dcgs.append(dcgs[i] + t * math.log(2)/math.log(2+i))
    
    return dcgs
    
def compute_DCG_values(predictions, targets, at):
    return [compute_DCG(t, p, at) for t, p in zip(predictions, targets)]

def compute_DCGs_values(predictions, targets, at):
    return [compute_DCGs(t, p, at) for t, p in zip(predictions, targets)]

#def compute(metric, predictions, targets):
#    if re.match('DCG@\d$', metric):
#        return DCG(predictions, targets, int(metric[-1])).compute()
#    elif re.match('NDCG@\d$', metric):
#        return NDCG(predictions, targets, int(metric[-1])).compute()
#    elif metric == 'NDCG@E': 
#        perfs = NDCG(predictions, targets, [1,3]).compute()
#        return (perfs[1] + perfs[3]) / 2
#
#
#def compute_DCG(prediction, target, at):
#    if isinstance(at, int):
#        at = [at]
#
#    docs = sorted(zip(prediction, target), 
#        reverse=True, key=lambda x: (x[0], -x[1]))[0:max(at)]
#
#    dcgs = [0]
#    for i, (p, t) in enumerate(docs):
#        dcgs[i+1] = dcgs[i-1] + t * math.log(2)/math.log(2+i)
#    
#    return dcgs
#
#class DCG(Metric):
#    def __init__(self, predictions, targets, at=3):
#        self.predictions = predictions 
#        self.targets = targets
#        
#    def average(self, func):
#        ave = {}
#        for p, t in zip(self.predictions, self.targets):
#            values = func(p, t)
#            for at in self.at:
#                ave[at] += values[at] / len(self.predictions)
#        
#        if len(self.at) == 1:
#            ave = ave[self.at]
#        
#        return ave
#    
#    def compute(self):
#        return self.average(self.compute_DCG)
#        
#class NDCG(DCG):
#    def compute_NDCG(self, prediction, target, at):
#        ndcgs = {}
#        for _at in at:
#            idcg = target.get_ideal_NDCG(_at)
#            if idcg == 0:
#                ndcgs[at] = 0
#            else:
#                ndcgs[at] = compute_DCG(prediction, target, at) / idcg
#        return ndcgs
#        
#    def compute(self, at):
#        
#        
#        
#        
#        return self.average(self.compute_NDCG)

# This class could be used to compute nDCG at 1, 2 or n.            
#class nDCG(Metric):
#    def __init__(self, predictions, targets, per_query=False, at=[1]):
#        self.predictions = predictions
#        self.targets = targets
#        self.per_query = per_query
#        self.at = at
#        
#    def compute(self):
#        ndcg = array([self.compute_nDCG(p, t) for p, t in zip(self.predictions, self.targets)])
#        
#        if not self.per_query:
#            ndcg = sum(ndcg) / len(dcg)
#        
#        if len(self.at) == 1 or isinstance(self.at, int):
#            ndcg = transpose(ndcg)[0]
#        
#        return ndcg
#        
#    def compute_DCG(self, prediction_set, target_set):
#        docs = sorted(zip(prediction_set, target_set), reverse=True)
#        
#        if '*' in self.at: 
#            self.at[self.at.index('*')] = len(target_set)
#        
#        dcg = [docs[0][1]]
#        for i, (p, t) in enumerate(docs[1:max(self.at)]):
#            dcg += t / math.log(i+2)
#        
#        return array([sum(dcg[:_at]) for _at in self.at])   
#    
#    # unefficient, note that the iDCG could be cached
#    def compute_nDCG(self, prediction_set, target_set):
#        return self.compute_DCG(prediction_set, target_set) / self.compute_DCG(target_set, target_set)