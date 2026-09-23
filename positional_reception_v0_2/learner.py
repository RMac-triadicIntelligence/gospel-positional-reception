"""Observable-only predictor. Does not import or read substrate/diagnostic files."""
import json
import sys
import numpy as np

OBS = {'impulse','t','x','x_lag_half','x_lag_one'}
META = {'trial_id','history_id','family'}
CLASSES = ['left','right','unresolved']
MODELS = ['offering','time','position','time_position','history']

def validate(rows, training=False):
    expected=OBS|META|({'label'} if training else set())
    for r in rows:
        if set(r)!=expected: raise ValueError('Unexpected or missing fields')
        if not all(np.isfinite(float(r[k])) for k in OBS): raise ValueError('Nonfinite input')
        if training and r['label'] not in CLASSES: raise ValueError('Unknown label')

def features(rows, model):
    if model not in MODELS: raise ValueError('Unknown model')
    out=[]
    for r in rows:
        v=[r['impulse']]
        if model in ['time','time_position','history']: v += [r['t']]
        if model in ['position','time_position','history']: v += [r['x']]
        if model=='history': v += [r['x']-r['x_lag_half'], r['x_lag_half']-r['x_lag_one']]
        out.append(v)
    return np.array(out,dtype=float)

class KNN:
    def fit(self,x,labels):
        if len(x)<15: raise ValueError('At least 15 training trials required')
        self.mean=x.mean(axis=0);self.scale=x.std(axis=0)
        self.scale=np.where(self.scale<1e-12,1.,self.scale)
        self.x=(x-self.mean)/self.scale
        self.y=np.array([CLASSES.index(v) for v in labels])
        return self
    def predict(self,x):
        out=[]
        for row in (x-self.mean)/self.scale:
            d=np.sum((self.x-row)**2,axis=1)
            ix=np.argsort(d,kind='stable')[:15]
            out.append(np.bincount(self.y[ix],minlength=3)/15)
        return np.array(out)

def run(data):
    if set(data)!={'train','test'}: raise ValueError('Unexpected dataset keys')
    validate(data['train'],True);validate(data['test'])
    a={r['history_id'] for r in data['train']};b={r['history_id'] for r in data['test']}
    if a&b: raise ValueError('History split leakage')
    predictions=[];fitted=[]
    for regime in ['mixed','forward_only']:
        train=[r for r in data['train'] if regime=='mixed' or r['family']=='forward']
        for model in MODELS:
            knn=KNN().fit(features(train,model),[r['label'] for r in train])
            ps=knn.predict(features(data['test'],model))
            fitted.append({'regime':regime,'model':model,'n_train':len(train),
                           'mean':knn.mean.tolist(),'scale':knn.scale.tolist()})
            for r,p in zip(data['test'],ps):
                predictions.append({'trial_id':r['trial_id'],'regime':regime,'model':model,
                                    'predicted':CLASSES[int(np.argmax(p))],'probabilities':p.tolist()})
    return {'predictions':predictions,'fitted':fitted}

if __name__=='__main__':
    with open(sys.argv[1]) as f:data=json.load(f)
    result=run(data)
    with open(sys.argv[2],'w') as f:json.dump(result,f,indent=2)
