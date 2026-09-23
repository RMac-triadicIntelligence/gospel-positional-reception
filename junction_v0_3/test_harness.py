"""Regression tests for the passing condition, separate from junction cases."""
import unittest
from dataclasses import replace
from unittest.mock import patch
import junction_v0_3 as j

class HarnessTests(unittest.TestCase):
    def verdict(self, expectation, fn):
        j.RESULTS.clear();j.case('probe',expectation,fn)
        self.assertEqual(len(j.RESULTS),1)
        return j.RESULTS[0][2]

    def test_text_and_truthy_values_are_not_success(self):
        for value in ['nothing executed','',True,False,None,1,{'ok':True}]:
            with self.subTest(value=value):
                self.assertEqual(self.verdict(j.COMPLETE,lambda:value),'FAIL')

    def test_unexpected_refusal_fails(self):
        def refuse():raise j.ConstitutionalViolation('refused')
        self.assertEqual(self.verdict(j.COMPLETE,refuse),'FAIL')
        self.assertEqual(self.verdict(j.OFFER_NO_CROSSING,refuse),'FAIL')
        self.assertEqual(self.verdict(j.REFUSE,refuse),'PASS')

    def test_runtime_error_is_not_expected_refusal(self):
        def broken():raise KeyError('expiry')
        self.assertEqual(self.verdict(j.REFUSE,broken),'FAIL')

    def test_compound_results_have_ordered_expectations(self):
        left=j.k_insufficient();right=j.k_sufficient()
        expected=(j.OFFER_NO_CROSSING,j.COMPLETE)
        self.assertEqual(self.verdict(expected,lambda:(left,right)),'PASS')
        self.assertEqual(self.verdict(expected,lambda:(right,left)),'FAIL')
        self.assertEqual(self.verdict(expected,lambda:(left,)),'FAIL')

    def test_record_flags_checked_without_truthiness(self):
        rec=j.k_sufficient()
        for bad in [replace(rec,offering_made=False),replace(rec,approval_valid=False),
                    replace(rec,restoration_completed='yes'),replace(rec,basin='left')]:
            self.assertEqual(self.verdict(j.COMPLETE,lambda:bad),'FAIL')

    def test_forced_disagreement_and_disabled_recorder(self):
        self.assertEqual(self.verdict(j.COMPLETE,j.k_criterion_disagreement),'PASS')
        real=j.JunctionOrganism.receive_offering
        def disabled(self,*args,**kwargs):
            rec=real(self,*args,**kwargs);rec.criterion_disagreement=False;return rec
        with patch.object(j.JunctionOrganism,'receive_offering',disabled):
            self.assertEqual(self.verdict(j.COMPLETE,j.k_criterion_disagreement),'FAIL')

    def test_observer_patch_is_restored(self):
        before=j.observe
        j.k_criterion_disagreement()
        self.assertIs(j.observe,before)

    def test_missing_components_reaches_receiver(self):
        real=j.JunctionOrganism.receive_offering;calls=[]
        def tracked(self,*args,**kwargs):
            calls.append(True);return real(self,*args,**kwargs)
        with patch.object(j.JunctionOrganism,'receive_offering',tracked):
            self.assertEqual(self.verdict(j.REFUSE,j.k_no_components_at_receive),'PASS')
        self.assertEqual(calls,[True])

if __name__=='__main__':unittest.main()
