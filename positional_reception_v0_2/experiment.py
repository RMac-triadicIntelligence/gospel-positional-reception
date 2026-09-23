import csv,json,random,hashlib,platform,subprocess,sys
from pathlib import Path
from dataclasses import asdict
import numpy as np
from substrate_v01 import State,History,evolve,observe,geometry,step,drift

ROOT=Path(__file__).parent
IMPULSES=[0,.3,.45,.6,.75,.9,1.05,1.2,1.35,1.5]
CHECKPOINTS=[2,6,12,24]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_csv(p,rows):
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def draw_history(seed,family):
    rng=random.Random(seed)
    phase=rng.uniform(-3.14,3.14);amp=rng.uniform(.005,.035)
    rate=rng.uniform(.08,.22);mag=rng.uniform(.18,.31)
    return History(target=mag*(1 if family=='forward' else -1),amplitude=amp,phase=phase,rate=rate)

def public_row(state,samples,impulse,history_id,trial_id,family):
    return {'trial_id':trial_id,'history_id':history_id,'family':family,
            'impulse':impulse,'t':round(state.t,8),'x':state.x,
            'x_lag_half':samples[.5],'x_lag_one':samples[1.]}

def generate():
    data={'train':[],'test':[]};truth=[];hidden=[]
    for split,seeds in [('train',range(30)),('test',range(1000,1012))]:
        for seed in seeds:
            for family in ['forward','reverse']:
                h=draw_history(seed,family);s=State();hist=f'{family}:{seed}'
                for t in CHECKPOINTS:
                    samples={}
                    for lag in [1.,.5,0.]:
                        s=evolve(s,h,t-lag-s.t);samples[lag]=s.x
                    for j,impulse in enumerate(IMPULSES):
                        tid=f'{hist}:{t}:{j}'
                        r=public_row(s,samples,impulse,hist,tid,family)
                        label,end=observe(s,h,impulse,frozen=False)
                        if split=='train':data['train'].append({**r,'label':label})
                        else:
                            data['test'].append(r)
                            truth.append({'trial_id':tid,'history_id':hist,'family':family,'label':label})
                            hidden.append({'trial_id':tid,'seed':seed,'family':family,
                                           'state':asdict(s),'history':asdict(h),'impulse':impulse,
                                           'label':label,'end':asdict(end)})
    return data,truth,hidden

def trace(seed,t,impulse,dt=.02):
    h=History(phase=random.Random(seed).uniform(-3.14,3.14))
    pre=evolve(State(),h,t,dt=dt)
    s0=geometry(pre.a)[1]
    s=State(pre.x+impulse,pre.a,pre.t);x0=s.x
    rows=[];encounter=None;previous=None
    def record(state,stage):
        boundary=geometry(state.a)[1]
        adot=h.rate*(h.evidence(state.t)-state.a)
        xdot=drift(state.x,state.a)
        sdot=-adot/(1-3*boundary*boundary)
        return {'stage':stage,'t':state.t,'x':state.x,'a':state.a,'boundary':boundary,
                'gap':boundary-state.x,'x_dot':xdot,'boundary_dot':sdot,'gap_dot':sdot-xdot,
                'state_displacement':state.x-x0,'boundary_displacement':boundary-s0,
                'gap_closure':(s0-x0)-(boundary-state.x)}
    rows.append(record(pre,'pre_impulse'));rows.append(record(s,'post_impulse'))
    for _ in range(round(24/dt)):
        previous=rows[-1];s=step(s,h,dt);row=record(s,'dwelling');rows.append(row)
        if encounter is None and previous['gap']>0>=row['gap']:
            encounter={'lower_t':previous['t'],'upper_t':row['t'],
                       'state_contribution':row['state_displacement'],
                       'boundary_contribution':-row['boundary_displacement'],
                       'gap_closure':row['gap_closure']}
    label,end=observe(pre,h,impulse,dt=dt,frozen=False)
    return rows,{'seed':seed,'checkpoint':t,'impulse':impulse,'initial_gap':s0-x0,
                 'outcome':label,'first_encounter':encounter,
                 'accounting_max_error':max(abs(r['gap_closure']-(r['state_displacement']-r['boundary_displacement'])) for r in rows[1:])}

def score(predictions,truth):
    index={r['trial_id']:r for r in truth}
    if len(index)!=len(truth):raise ValueError('Duplicate truth ID')
    expected={(t['trial_id'],reg,model) for t in truth for reg in ['mixed','forward_only']
              for model in ['offering','time','position','time_position','history']}
    seen=set();joined=[]
    for p in predictions:
        key=(p['trial_id'],p['regime'],p['model'])
        if key not in expected or key in seen:raise ValueError('Unexpected/duplicate prediction')
        seen.add(key);t=index[p['trial_id']];probs=p['probabilities']
        if len(probs)!=3 or not all(np.isfinite(v) and 0<=v<=1 for v in probs) or abs(sum(probs)-1)>1e-9:raise ValueError('Invalid probabilities')
        if p['predicted']!=['left','right','unresolved'][int(np.argmax(probs))]:raise ValueError('Label/probability inconsistency')
        y=['left','right','unresolved'].index(t['label'])
        joined.append({**t,'regime':p['regime'],'model':p['model'],'predicted':p['predicted'],
                       'correct':int(t['label']==p['predicted']),
                       'brier':sum((v-int(i==y))**2 for i,v in enumerate(probs))})
    if seen!=expected:raise ValueError('Missing predictions')
    metrics=[];per_history=[]
    for reg in ['mixed','forward_only']:
        for model in ['offering','time','position','time_position','history']:
            rr=[r for r in joined if r['regime']==reg and r['model']==model]
            for group in ['all','forward','reverse']:
                sub=[r for r in rr if group=='all' or r['family']==group]
                metrics.append({'regime':reg,'model':model,'group':group,'n':len(sub),
                                'accuracy':sum(r['correct'] for r in sub)/len(sub),
                                'brier':sum(r['brier'] for r in sub)/len(sub),
                                'unresolved':sum(r['label']=='unresolved' for r in sub),
                                'right':sum(r['label']=='right' for r in sub)})
            for hid in sorted({r['history_id'] for r in rr}):
                sub=[r for r in rr if r['history_id']==hid]
                per_history.append({'regime':reg,'model':model,'history_id':hid,'family':sub[0]['family'],
                                    'accuracy':sum(r['correct'] for r in sub)/len(sub),
                                    'brier':sum(r['brier'] for r in sub)/len(sub)})
    paired=[]
    for r in per_history:
        if r['model']=='history':
            base=next(b for b in per_history if b['model']=='time_position' and b['regime']==r['regime'] and b['history_id']==r['history_id'])
            paired.append({'regime':r['regime'],'history_id':r['history_id'],'family':r['family'],
                           'brier_improvement':base['brier']-r['brier']})
    return metrics,per_history,paired

def main():
    out=ROOT/'results';out.mkdir(exist_ok=True)
    data,truth,hidden=generate()
    (out/'observable_dataset.json').write_text(json.dumps(data))
    (out/'heldout_truth.json').write_text(json.dumps(truth))
    (out/'diagnostic_hidden.json').write_text(json.dumps(hidden))
    # The learner receives no truth or diagnostic filename.
    subprocess.run([sys.executable,str(ROOT/'learner.py'),str(out/'observable_dataset.json'),str(out/'predictions.json')],check=True)
    pred_hash=digest(out/'predictions.json')
    prediction=json.loads((out/'predictions.json').read_text())
    # Scoring begins only after the predictions artifact exists.
    truth=json.loads((out/'heldout_truth.json').read_text())
    metrics,hmetrics,paired=score(prediction['predictions'],truth)
    write_csv(out/'metrics.csv',metrics);write_csv(out/'per_history.csv',hmetrics);write_csv(out/'paired_improvements.csv',paired)
    diagnostics=[]
    for seed,t,impulse in [(3,24,.45),(5,2,.85),(10,2,.85)]:
        rows,result=trace(seed,t,impulse);write_csv(out/f'trace_seed_{seed}.csv',rows)
        _,fine=trace(seed,t,impulse,.01)
        result['half_step']=fine;diagnostics.append(result)
    numerical=[]
    for r in random.Random(802).sample(hidden,24):
        label,end=observe(State(**r['state']),History(**r['history']),r['impulse'],dt=.01,frozen=False)
        numerical.append({'trial_id':r['trial_id'],'same_label':label==r['label'],
                          'end_x_delta':abs(end.x-r['end']['x'])})
    write_csv(out/'numerical_checks.csv',numerical)
    summary={'scope':'Observable prediction in the supplied dynamical family; no developmental reception or authorization claim.',
             'runtime':{'python':platform.python_version(),'numpy':np.__version__},
             'train_trials':len(data['train']),'heldout_trials':len(data['test']),
             'prediction_sha256_before_scoring':pred_hash,'diagnostics':diagnostics,
             'half_step_label_changes':sum(not r['same_label'] for r in numerical),
             'half_step_max_end_x_delta':max(r['end_x_delta'] for r in numerical),
             'protocol_sha256':digest(ROOT/'PROTOCOL.md')}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    for m in metrics:
        if m['model'] in ['time_position','history']:print(m)
if __name__=='__main__':main()
