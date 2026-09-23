#!/usr/bin/env python3
import csv, hashlib, json, platform, random
from pathlib import Path
from dataclasses import asdict
from reception import State, History, evolve, capacity, predict, observe

OUT=Path(__file__).parent/'results'
def main():
    OUT.mkdir(exist_ok=True)
    rows=[]; snapshots=[]
    for seed in range(12):
        rng=random.Random(seed)
        phase=rng.uniform(-3.14,3.14)
        for arm,target in [('forward',.31),('reverse',-.20),('fixed_landscape',0.0)]:
            h=History(target=target,amplitude=0 if arm=='fixed_landscape' else .015,phase=phase)
            s=State()
            for checkpoint in [0,2,6,12,24]:
                if checkpoint>s.t: s=evolve(s,h,checkpoint-s.t)
                cap=capacity(s)
                snapshot={'seed':seed,'arm':arm,**asdict(s),**cap}
                snapshots.append(snapshot)
                # Predictions precede all corresponding assay observations.
                for impulse in [0,.2,.45,.6,.85,-.6]:
                    prediction=predict(s,impulse)
                    for frozen in [True,False]:
                        outcome,end=observe(s,h,impulse,frozen=frozen)
                        rows.append({**snapshot,'impulse':impulse,'assay':'frozen_clone' if frozen else 'continued_dwelling',
                                     'prediction':prediction,'observed':outcome,'end_x':end.x,'end_a':end.a,
                                     'matches':prediction==outcome})
    def save_csv(name,data):
        with (OUT/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    save_csv('trials.csv',rows);save_csv('snapshots.csv',snapshots)
    counts={}
    for kind in ['frozen_clone','continued_dwelling']:
        sub=[r for r in rows if r['assay']==kind]
        counts[kind]={'n':len(sub),'matches':sum(r['matches'] for r in sub),
                      'unresolved':sum(r['observed']=='unresolved' for r in sub),
                      'mismatches':[{'seed':r['seed'],'arm':r['arm'],'t':r['t'],'impulse':r['impulse'],
                                     'prediction':r['prediction'],'observed':r['observed']} for r in sub if not r['matches']]}
    # Time-step convergence is assessed on outcomes and terminal coordinates.
    max_delta=0.; flips=0
    convergence_sample=random.Random(917).sample(rows,72)
    for r in convergence_sample:
        h=History(target={'forward':.31,'reverse':-.2,'fixed_landscape':0}[r['arm']],
                  amplitude=0 if r['arm']=='fixed_landscape' else .015,
                  phase=random.Random(r['seed']).uniform(-3.14,3.14))
        s=State(r['x'],r['a'],r['t'])
        label,end=observe(s,h,r['impulse'],dt=.01,frozen=r['assay']=='frozen_clone')
        max_delta=max(max_delta,abs(end.x-r['end_x']))
        flips+=label!=r['observed']
    summary={'scope':'Constructed scalar landscape instrument; no learned semantics, authorization, burden or forgiveness mechanism.',
             'runtime':platform.python_version(),'seeds':list(range(12)),'dt':.02,'assay_duration':24,
             'counts':counts,'convergence':{'sample_n':len(convergence_sample),'dt_half':.01,'max_end_x_delta':max_delta,'label_flips':flips},
             'sources':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:{key:value for key,value in v.items() if key!='mismatches'} for k,v in counts.items()},indent=2))
    print(summary['convergence'])
if __name__=='__main__':main()
