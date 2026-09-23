# Positional reception v0.1

A first executable investigation of §4.5, “The correction must remain exposed to correction.” Raised, Not Rented. Prepared by ChatGPT at Rusty Williams McMurray's request, 10 September 2026.

## Run

Python 3.10+; standard library only. From this directory:

```sh
python run_experiment.py
python -m unittest discover -s . -v
```

The first command writes results/trials.csv, results/snapshots.csv, and results/summary.json. The supplied results were executed, not illustrative numbers. The second runs seven implementation checks. A passing check is not support for a grace, forgiveness, or developmental-intelligence hypothesis.

## What Rusty specified

There is no separate waiting mode: there is dwelling. During dwelling the basin's topography changes. Capacity can be recognized before crossing: a sufficiently small nudge may carry an organism that is close enough to a separatrix across it. Prior discussion also requires external authorization and distinguishes binary approval from reception; this isolated instrument does not implement those requirements.

## What ChatGPT chose for this first code

Every live integration step is dwelling. Two continuous coordinates are stored: position x and landscape tilt a; t records elapsed simulation time. No readiness score, restored status, mercy field, guilt variable, or success-triggered decrement is present.

The chosen potential is:

V(x,a) = x^4/4 - x^2/2 - a*x

dx/dt = x - x^3 + a

da/dt = 0.15 * (q(t) - a)

q(t) = target + amplitude*sin(0.35*t + phase).

This landscape evolution is programmed, not learned or inferred from an organism's meaningful experience. Its relaxation form is a modeling choice, not a discovered law of dwelling. Neither the target nor the perturbation represents a measured relationship. Forward, reverse, and fixed-landscape controls differ in target (+0.31, -0.20, 0). The fixed-landscape control still evolves under the same dynamics; it is an ablation, not a new “waiting” state in the proposed architecture. Fixed-landscape amplitude is zero; other amplitudes are 0.015. Twelve seeds select phases, not stochastic outcomes. Trials sharing a history are not independent samples.

All chosen histories preserve two wells: |a| remains below 2/(3*sqrt(3)). The middle stationary point is the separatrix of the frozen one-dimensional flow. Positive tilt moves both the attractor and boundary; the code does not silently equate boundary movement with organism movement. `snapshots.csv` retains both.

## Pre-offering measurement

For a snapshot in the left basin, capacity is operationalized as the infimum positive positional impulse needed to reach the frozen boundary: middle_root(a) - x. An impulse strictly larger than that value predicts the right basin. Equality is unresolved, not a successful crossing. Negative impulses are retained as a direction control. The potential barrier is separately recorded; it is not equated with positional distance or psychological cost.

This is a model-based observation using privileged access to x and a. It does not establish that an external observer could recover these quantities from an opaque AI's behavior. The predictor uses roots of the vector field. The assay independently integrates the perturbed copy and classifies its terminal location by attractor proximity and low drift; it never assigns the predicted label as the observed outcome.

Two assays are run from each immutable snapshot:

1. Frozen diagnostic clone: a is fixed for the short assay. This tests the local geometrical measurement, not a mode of live existence.
2. Continued dwelling: a continues developing under the same history drive while the clone responds to the impulse.

Important: the instantaneous frozen separatrix is NOT asserted to be the true boundary of the evolving, time-dependent system. A frozen prediction can fail under continued dwelling. Those failures are evidence about the insufficiency of the measurement, not renamed “unreadiness.”

## Scope

This code models the response to an externally applied impulse, not who may authorize one. It neither integrates with nor replaces Article II, existing keys, signed grants, event binding, or organism identity. Do not treat the impulse method as a protected production transition.

There is no confession, realization verification, burden elimination, truthful-memory integration, relationship learning, or semantic parable interpretation here. No result demonstrates grace or identifies a Gospel narrative with these equations. Crossing is an operational transition between attractor neighborhoods, not a claim about redemption. The experiment is a small inspectable substrate for challenging one candidate reception measure.

## Files

- reception.py: immutable snapshots, explicit dynamics, pre-offering measurement and numerical assay.
- run_experiment.py: deterministic sweep, paired controls, raw records and convergence sample.
- test_reception.py: independent boundary cases, direction of development, clone integrity, no-nudge behavior, loss-of-bistability rejection, and a repeated-impulse counterexample.
- FINDINGS.md: executed results and limits.
- results/: raw trials, snapshots, runtime/source hashes and test output.
- manifest.json: artifact hashes.

No new license is assigned. Existing source artifacts were not edited.
