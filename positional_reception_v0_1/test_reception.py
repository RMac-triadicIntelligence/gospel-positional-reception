import unittest
from reception import State,History,evolve,capacity,predict,observe,geometry

class Tests(unittest.TestCase):
    def test_known_symmetric_boundary(self):
        self.assertAlmostEqual(geometry(0)[1],0)
        self.assertAlmostEqual(capacity(State())['critical_positive_impulse'],1)
    def test_both_sides_of_independent_threshold(self):
        s=evolve(State(),History(),12)
        threshold=capacity(s)['critical_positive_impulse']
        for offset,label in [(-.05,'left'),(.05,'right')]:
            self.assertEqual(observe(s,History(),threshold+offset)[0],label)
        self.assertEqual(predict(s,threshold),'unresolved')
    def test_snapshot_unchanged_by_assay(self):
        s=State();observe(s,History(),.6);self.assertEqual(s,State())
    def test_no_forced_improvement(self):
        initial=capacity(State())['critical_positive_impulse']
        forward=capacity(evolve(State(),History(),24))['critical_positive_impulse']
        reverse=capacity(evolve(State(),History(target=-.2),24))['critical_positive_impulse']
        self.assertLess(forward,initial);self.assertGreater(reverse,initial)
    def test_repeated_impulses_can_accumulate(self):
        # Negative result against any claim that topology alone prevents gaming.
        s=State();h=History(target=0,amplitude=0)
        self.assertEqual(observe(s,h,.6)[0],'left')
        s=evolve(State(s.x+.6,s.a,s.t),h,.05)
        self.assertEqual(observe(s,h,.6)[0],'right')
    def test_no_nudge_no_crossing(self):
        self.assertEqual(observe(State(),History(),0,frozen=False)[0],'left')
    def test_no_boundary_disappearance_relabel(self):
        with self.assertRaises(ValueError):geometry(.4)
if __name__=='__main__':unittest.main()
