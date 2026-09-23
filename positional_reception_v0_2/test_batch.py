import ast,json,unittest
from pathlib import Path
import numpy as np
from learner import validate,features,KNN,run
from experiment import score,trace

ROOT=Path(__file__).parent

def row(i=0,label=False):
    r={'trial_id':str(i),'history_id':f'h{i}','family':'forward',
       'impulse':i/20,'t':2.,'x':-1.,'x_lag_half':-1.1,'x_lag_one':-1.2}
    if label:r['label']='left' if i<10 else 'right'
    return r

class IsolationTests(unittest.TestCase):
    def test_hidden_field_rejected(self):
        for key in ['a','potential','separatrix','future_x','label']:
            r=row();r[key]=0
            with self.assertRaises(ValueError):validate([r])
    def test_hidden_state_does_not_change_public_row(self):
        from experiment import public_row
        from substrate_v01 import State
        samples={.5:-1.1,1.:-1.2}
        a=public_row(State(-1,0,2),samples,.6,'h','t','forward')
        b=public_row(State(-1,.3,2),samples,.6,'h','t','forward')
        self.assertEqual(a,b)
    def test_missing_observation_rejected(self):
        r=row();del r['x_lag_one']
        with self.assertRaises(ValueError):validate([r])
    def test_nonfinite_rejected(self):
        r=row();r['x']=float('nan')
        with self.assertRaises(ValueError):validate([r])
    def test_metadata_not_features(self):
        a=row();b={**a,'history_id':'secret','family':'reverse','trial_id':'changed'}
        for name in ['offering','time','position','time_position','history']:
            np.testing.assert_array_equal(features([a],name),features([b],name))
    def test_history_information_added(self):
        a=row();b={**a,'x_lag_half':-1.5}
        np.testing.assert_array_equal(features([a],'time_position'),features([b],'time_position'))
        self.assertFalse(np.array_equal(features([a],'history'),features([b],'history')))
    def test_training_only_scaling(self):
        train=np.arange(40,dtype=float).reshape(20,2)
        m=KNN().fit(train,['left']*20)
        before=m.mean.copy();scale=m.scale.copy()
        m.predict(np.array([[1e6,1e6]]))
        np.testing.assert_array_equal(m.mean,train.mean(axis=0))
        np.testing.assert_array_equal(m.mean,before);np.testing.assert_array_equal(m.scale,scale)
    def test_deterministic(self):
        d={'train':[row(i,True) for i in range(20)],'test':[row(100)]}
        self.assertEqual(run(d),run(d))
    def test_history_overlap_rejected(self):
        d={'train':[row(i,True) for i in range(20)],'test':[row()]}
        with self.assertRaises(ValueError):run(d)
    def test_import_allowlist(self):
        tree=ast.parse((ROOT/'learner.py').read_text())
        modules=set()
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):modules.update(a.name for a in n.names)
            elif isinstance(n,ast.ImportFrom):modules.add(n.module)
        self.assertEqual(modules,{'json','sys','numpy'})

class ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'results/observable_dataset.json').read_text())
        cls.truth=json.loads((ROOT/'results/heldout_truth.json').read_text())
        cls.pred=json.loads((ROOT/'results/predictions.json').read_text())['predictions']
    def test_complete_history_holdout(self):
        train={r['history_id'] for r in self.data['train']}
        test={r['history_id'] for r in self.data['test']}
        self.assertFalse(train&test);self.assertEqual(len(train),60);self.assertEqual(len(test),24)
        self.assertEqual(len(self.data['train']),2400);self.assertEqual(len(self.data['test']),960)
        for h in train|test:
            rows=self.data['train'] if h in train else self.data['test']
            self.assertEqual(sum(r['history_id']==h for r in rows),40)
    def test_heldout_observable_schema(self):validate(self.data['test'])
    def test_both_directions_have_both_outcomes(self):
        for family in ['forward','reverse']:
            labels={r['label'] for r in self.truth if r['family']==family}
            self.assertTrue({'left','right'}<=labels)
    def test_missing_prediction_is_harness_error(self):
        with self.assertRaises(ValueError):score(self.pred[:-1],self.truth)
    def test_duplicate_prediction_is_harness_error(self):
        with self.assertRaises(ValueError):score(self.pred+[self.pred[0]],self.truth)
    def test_invalid_probability_is_harness_error(self):
        p=[{**self.pred[0],'probabilities':[float('nan'),0,1]}]+self.pred[1:]
        with self.assertRaises(ValueError):score(p,self.truth)
    def test_label_probability_inconsistency_rejected(self):
        bad='right' if self.pred[0]['predicted']=='left' else 'left'
        p=[{**self.pred[0],'predicted':bad}]+self.pred[1:]
        with self.assertRaises(ValueError):score(p,self.truth)
    def test_truth_permutation_does_not_change_predictions(self):
        before=json.dumps(self.pred,sort_keys=True)
        altered=[{**r,'label':'left' if r['label']=='right' else 'right'} for r in self.truth]
        original_metrics=score(self.pred,self.truth)[0]
        altered_metrics=score(self.pred,altered)[0]
        self.assertEqual(before,json.dumps(self.pred,sort_keys=True))
        self.assertNotEqual(original_metrics,altered_metrics)
    def test_three_misses_and_gap_accounting(self):
        for seed,t,k in [(3,24,.45),(5,2,.85),(10,2,.85)]:
            rows,result=trace(seed,t,k)
            self.assertGreater(result['initial_gap'],0)
            self.assertEqual(result['outcome'],'right')
            self.assertIsNotNone(result['first_encounter'])
            self.assertLess(result['accounting_max_error'],1e-12)
            self.assertAlmostEqual(rows[0]['gap']-rows[1]['gap'],k,12)
            e=result['first_encounter']
            self.assertAlmostEqual(e['state_contribution']+e['boundary_contribution'],e['gap_closure'],12)
    def test_boundary_velocity_finite_difference(self):
        from substrate_v01 import geometry
        rows,_=trace(5,2,.85)
        for r in rows[2::100]:
            # Check implicit derivative against independent nearby root evaluations.
            eps=1e-6
            derivative=(geometry(r['a']+eps)[1]-geometry(r['a']-eps)[1])/(2*eps)
            implicit=-1/(1-3*r['boundary']**2)
            self.assertAlmostEqual(derivative,implicit,7)

if __name__=='__main__':unittest.main()
