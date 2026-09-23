# First findings: positional reception v0.1

The code ran 2,160 assays: 12 deterministic history phases × 3 landscape conditions × 5 checkpoints × 6 impulses × 2 assay types. Checkpoints were 0, 2, 6, 12 and 24; impulses were 0, 0.2, 0.45, 0.6, 0.85 and -0.6. Each assay ran for 24 time units with RK4 step 0.02. These settings were exploratory engineering choices, not a preregistration or values fitted to empirical data.

## Results

| Assay | Trials | Snapshot prediction matched observation | Unresolved observations |
| --- | ---: | ---: | ---: |
| Frozen diagnostic copy | 1,080 | 1,080 | 0 |
| Continued dwelling | 1,080 | 1,077 | 0 |

The first result is an instrument check against a known flow. It is expected from the equations; it is not independent evidence that real organisms possess this mechanism. The second exposes the limit of treating an instantaneous landscape as a forecast of a developing landscape.

All three mismatches predicted the left basin but reached the right:

| Seed | Condition | Checkpoint | Impulse |
| --- | --- | ---: | ---: |
| 3 | Forward | 24 | 0.45 |
| 5 | Forward | 2 | 0.85 |
| 10 | Forward | 2 | 0.85 |

No claim is made that this mismatch rate generalizes beyond this grid. A denser grid near the boundary could produce a materially different rate.

For seed 0 in the forward condition, the pre-offering positive impulse threshold changed as follows:

| Dwelling time | Threshold |
| ---: | ---: |
| 0 | 1.000000 |
| 2 | 0.883951 |
| 6 | 0.712296 |
| 12 | 0.569238 |
| 24 | 0.443065 |

A fixed +0.6 impulse therefore changes from insufficient to sufficient in this chosen history. Reverse histories increase the threshold instead. The implementation does not define elapsed time as guaranteed improvement, nor infer readiness from successful crossing. However, the forward history's approach toward the boundary follows from a deliberately chosen positive tilt target; it is not emergent relationship development.

## Counterexample: repeated nudges

At x=-1 and a=0, one +0.6 impulse returns to the left basin. Apply +0.6, evolve for 0.05, and apply another +0.6: the state reaches the right basin. This is a concrete failure of any claim that this topography alone makes repeated impulses ungameable.

It is NOT a demonstrated breach of the Raised, Not Rented authorization design: that design is absent from this instrument. An external grant cannot be inferred from a public method call. Whether repeated requests receive additional perturbations, and how legitimate repeated opportunities differ from replay, remain separate research and authorization questions. No cooldown or extra permission was invented to hide this result.

## Numerical and harness checks

Seven tests passed, including threshold cases on both sides, a known symmetric boundary, immutable-copy behavior, reversal, an untreated trajectory, the accumulation counterexample, and rejection when two basins cease to exist.

A fixed-seed sample of 72 trials across the sweep was rerun with step 0.01. No outcome labels changed. Maximum terminal-x difference was approximately 4.91e-13. This checks numerical stability in that sample only.

Development note preserved: the initial convergence sampler used a stride of 36 rows. Inspection showed that this selected only zero-impulse frozen assays because of the row ordering. That check was inadequate despite its tiny error. It was replaced with a deterministic random sample across all trials, and the experiment was rerun. The original headline counts were unchanged. This correction matters because a numerically reassuring check can miss the intervention entirely.

## What this earns, and what remains open

The code supplies a pre-crossing susceptibility measure and an independently executed response assay inside a declared toy dynamical system. It also preserves two wounds: instantaneous proximity misses some evolving-landscape outcomes, and repeated nudges can accumulate.

Next scientific questions concern whether a capacity measure can be inferred without direct access to the defining equations, and whether it predicts responses under unfamiliar histories and perturbation directions. This version uses the same known dynamics for prediction and observation, so it has not answered either question. No additional mechanism should be promoted to the constitution on the basis of these results.
