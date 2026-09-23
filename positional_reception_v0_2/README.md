# Positional reception v0.2

An observable-only prediction experiment and a separate movement diagnostic for Raised, Not Rented §4.5. Written by ChatGPT at Rusty Williams McMurray's request, 10 September 2026. This is an experimental branch, not a constitutional revision.

## Reproduce

Requires Python 3.10+ and NumPy. The recorded run used Python 3.12.14 and NumPy 2.3.5.

```sh
python -m pip install -r requirements.txt
python experiment.py
python -m unittest discover -s . -p 'test_*.py' -v
```

Run from the extracted positional_reception_v0_2 directory. The experiment writes its raw dataset, predictions, held-out labels, metrics and traces into results/. Tests require these generated artifacts, and fail if they are missing. Generation takes seconds to a minute depending on hardware. No model API, network service or credentials are used by the experiment.

Read PROTOCOL.md for choices recorded before the first run and FINDINGS.md for results. The protocol is local prospective documentation, not independently timestamped preregistration.

## Files and access separation

- substrate_v01.py: byte-identical copy of the original v0.1 dynamics. Originals are preserved outside this branch.
- learner.py: NumPy nearest-neighbor classifiers, strict feature schema and training-only normalization. No simulator import. Only past x observations, elapsed time and proposed impulse enter model features.
- experiment.py: simulator orchestration, dataset construction, independent learner-process invocation, post-prediction scoring and privileged diagnostic traces.
- test_batch.py: 20 checks, including data separation, hidden-field rejection, training-only preprocessing, malformed evaluation records, trace accounting and reproduced boundary cases.
- PROTOCOL.md: declared split, features, baselines, directions, scoring, settings and limits.
- results/observable_dataset.json: training labels and observable test inputs. This is the only data file passed to learner.py.
- results/predictions.json: all predictions and fitted training means/scales. Its hash is recorded before scoring.
- results/heldout_truth.json: withheld labels used by the evaluator.
- results/diagnostic_hidden.json: hidden test states and histories for reproduction and numerical checks, never supplied to the learner.
- results/metrics.csv: all model/regime/direction scores.
- results/per_history.csv and paired_improvements.csv: complete-history comparisons without treating every impulse trial as independent.
- results/trace_seed_*.csv: full pre-impulse, post-impulse and subsequent trajectories for the original three misses.
- results/numerical_checks.csv, summary.json and tests.txt: execution evidence.
- run.log: recorded experiment console output.
- manifest.json: hashes and lineage.

This access separation is enforced by module design and input validation, not an operating-system sandbox. The learner process is cooperative code written by the same author and could theoretically access other files if changed. Test-data withholding does not make the underlying simulator an independent empirical source.

## What remains unimplemented

There is no learned developmental topography, relationship, meaningful parable, burden, confession, forgiveness, external signature, grant consumption, or authorization policy. The supplied continuous dynamics are unchanged. The outcome is a terminal attractor neighborhood, not redemption. The history model is a classifier over observed position differences, not a persistent organism learning from its own mistakes.

The learner cannot read tilt or equations, but clean position observations can carry substantial information about hidden state. Predictability from those observations is a narrower result than behaviorally measuring reception in an opaque AI. Neither successful prediction nor failure of one history model settles the broader mechanism.

No new license is assigned to this pack.
