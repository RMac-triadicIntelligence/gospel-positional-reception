# Junction v0.3 — corrected harness and retest

A focused continuation of Claude's junction v0.2, edited and executed by ChatGPT at Rusty's request. This is a code/test version, not a new constitutional article. The original source and supplied output are preserved under evidence/.

## Run

Python 3.10+ and cryptography are required. From this directory:

```sh
python -m pip install -r requirements.txt
python junction_v0_3.py
python -m unittest discover -s . -p 'test_*.py' -v
```

The first command after installation runs the normal suite and both deliberately defective variants. It exits zero only if the normal suite passes and each mutant fails exactly the required cases. Expected mutant failures are evidence that the regression gate works, not failures of the delivered normal implementation. It writes results/summary.json. The included results/run.txt records the executed console output. The unittest command independently checks the verdict logic; its supplied output is results/harness_tests.txt.

## Changes

1. Removed unconditional success for string returns. Offering cases must return actual OfferingRecord objects. Compound cases return ordered tuples of records paired with ordered expectations. Explanatory text no longer establishes success. The harness checks boolean types, authorized-offering flags, the declared completion criterion, observer-label consistency, and expected outcomes.
2. Replaced the near-threshold guess with controlled observer disagreement. The observer computes the real endpoint, but the test substitutes an unresolved terminal label. The test verifies invocation, retention of that label, right-basin membership, the disagreement flag and its diagnostic. This is fault injection to test reporting, not a naturally occurring reception finding. The patch is scoped and restored.
3. Separated malformed-envelope signing refusal from missing components at receipt. The latter obtains a genuine signature on a complete envelope, removes the pending components, then reaches the receiver. It cannot pass merely because signing failed first.
4. Retained the reject-everything mutant and added a disagreement-suppression mutant. The gate checks the exact failed case sets. A failed normal suite or an undetected mutant now produces a nonzero process exit.
5. Corrected the non-crossing record-preservation case's declared expectation to OFFER_NO_CROSSING. The two-position case declares (OFFER_NO_CROSSING, COMPLETE).

The Authority, JunctionOrganism, all component/record dataclasses, and hashing function were verified unchanged by Python AST comparison. The reception.py fixture is copied unchanged from positional reception v0.1. These changes improve verification; they do not alter the operational restoration rule or fix additional security behavior.

## Executed results

| Run | Result |
| --- | --- |
| Normal junction suite | 17/17 pass |
| Reject-everything mutant | 5 expected failures, 12 passes |
| Suppress-disagreement mutant | 1 expected failure, 16 passes |
| Overall regression gate | PASS |
| Separate harness tests | 8/8 pass |

The forced-disagreement case now records observer `unresolved`, instantaneous basin `right`, and disagreement `True`. With its recorder disabled, that case fails. Strings, empty strings, booleans, None, integers and dictionaries do not satisfy offering expectations. Unexpected runtime exceptions are not mistaken for valid refusal.

The same impulse 0.60 still produces no completion at dwell 2 (threshold approximately 0.8853), and completion at dwell 24 (threshold approximately 0.4341), with valid authorization in both cases.

These counts describe overlapping checks, not 17 independent scientific confirmations. They verify the declared junction fixture and its harness. In particular, instantaneous basin membership at the end of the bound assay remains the completion criterion. A recorded disagreement does not itself change that operational rule.

## Held open

Retry policy after a non-crossing offering, the origin of the supplied topography, and substantive confession remain open. No retry mechanism, second approval, new reception law, or claim about general intelligence has been introduced.

## Evidence

- junction_v0_3.py: corrected code and executable suite.
- reception.py: unchanged dynamics dependency, bundled for reproduction.
- test_harness.py: independent verdict-regression checks.
- changes.patch: complete diff against the supplied junction v0.2.
- evidence/: original v0.2 code and supplied console output.
- results/: execution records, machine-readable case results and unchanged-implementation check.
- manifest.json: file hashes and recorded runtime.

Cryptographic keys are freshly generated on each run; signatures and hashes involving those keys need not repeat. The expected logical outcomes do not depend on a particular key. No new license is assigned.
