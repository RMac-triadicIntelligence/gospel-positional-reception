# Positional reception v0.2 — executed findings

## The result

Current position plus the proposed impulse was the strongest tested predictor. Adding elapsed time or recent position history did not improve it. This is a negative result for the added-history features with this fixed learner and dataset, not evidence that memory or dwelling is generally unnecessary.

The three original snapshot misses also received a direct movement analysis. At each first sampled boundary encounter, the state had moved left after the impulse, away from its initial boundary location; the instantaneous boundary had moved farther left and overtaken it. The narrow “boundary comes to the organism” interpretation is supported for these cases by the recorded displacements. It is not generalized to all crossings or to a true invariant boundary of the nonautonomous system.

## Design and run

The inherited simulator is unchanged. We sampled 30 training parameter sets and 12 held-out sets, each instantiated in forward and reverse directions. That produces 60 complete training histories and 24 complete held-out histories, but only 12 independent held-out parameter draws; direction pairs share parameters. Four checkpoints and ten impulses per history produce 2,400 training and 960 held-out trials. Both directions contain crossing and non-crossing outcomes. No terminal observation was unresolved in this run; the third outcome is nonetheless retained in the code and scoring.

The learner receives past position samples, elapsed time and the proposed impulse. It does not receive tilt, potential, roots or future observations. All five models use fixed k=15 nearest-neighbor prediction and training-only standardization. The history model adds two recent position increments to the time-plus-position baseline. No hyperparameters were searched or changed after seeing scores.

Two regimes were declared before evaluation: mixed-direction training, and forward-only training. Both are evaluated on the same untouched test histories. Forward-only training on reverse tests is direction-shift extrapolation; mixed training on held-out reverse histories is within-family generalization. They should not be conflated.

Predictions were saved and hashed before evaluation. This prevents the scoring function from choosing predictions after joining labels; it does not constitute independent scientific blinding. All modules and the simulator were authored together.

## Mixed-direction training

Every row below also knows the proposed impulse. Brier score is the sum of squared probability errors across three outcome classes; lower is better.

| Observations added to impulse | Forward accuracy | Reverse accuracy | Combined accuracy | Combined Brier |
| --- | ---: | ---: | ---: | ---: |
| None | 83.33% | 81.88% | 82.60% | 0.225139 |
| Time | 93.33% | 71.88% | 82.60% | 0.203028 |
| Current position | 99.38% | 99.79% | 99.58% | 0.007546 |
| Time + position | 98.75% | 99.38% | 99.06% | 0.017685 |
| Time + position + recent history | 98.54% | 98.75% | 98.65% | 0.030880 |

The position model made four errors among 960 trials, time-plus-position made nine, and the history model made thirteen. The history model had worse Brier score than time-plus-position in 11 of 12 forward histories and all 12 reverse histories. Mean paired Brier improvement (baseline minus history; positive would favor history) was -0.011389 forward and -0.015000 reverse.

Elapsed time alone is insufficient here. But recent increments have not earned value beyond current position with the chosen feature scaling, finite training sample, and nearest-neighbor learner. Adding features changes neighborhood geometry; this is not an information-theoretic proof that history contains no useful information. Position's strong result may reflect how closely it tracks the supplied evolving landscape, rather than an independently learned concept of reception.

## Forward-only training: reverse-history transfer

| Model | Held-out forward accuracy | Held-out reverse accuracy | Reverse Brier |
| --- | ---: | ---: | ---: |
| Impulse only | 90.83% | 71.88% | 0.544722 |
| Time | 94.58% | 66.88% | 0.640722 |
| Position | 99.38% | 81.88% | 0.263722 |
| Time + position | 99.17% | 81.88% | 0.276852 |
| Recent-history model | 98.54% | 71.25% | 0.366444 |

Recent-history features did not rescue reverse-direction transfer. Their Brier score was worse than time-plus-position in every forward and every reverse test history under this training regime. This is why keeping the reverse set and reporting it separately mattered. An aggregate accuracy would obscure the direction-shift failure.

The near-perfect within-family position result must not be described as general reception recognition: it falls materially when the training direction excludes the test direction.

## Boundary and state contributions

Let g=s(a)-x. Relative to the post-impulse snapshot, exact finite-displacement accounting is:

initial gap - current gap = state displacement - boundary displacement.

The impulse is recorded separately. The table uses the first dt=.02 sample with nonpositive gap, so a small overshoot beyond zero is expected.

| Original seed | Initial post-impulse gap | State contribution to closure | Boundary contribution to closure | Total gap closure |
| --- | ---: | ---: | ---: | ---: |
| 3 | 0.006568 | -0.012883 | +0.019480 | 0.006597 |
| 5 | 0.032262 | -0.052334 | +0.084940 | 0.032606 |
| 10 | 0.033273 | -0.066941 | +0.100535 | 0.033594 |

All three state contributions oppose gap closure; boundary movement more than compensates. First encounters are bracketed at absolute times [28.50,28.52], [4.72,4.74], and [5.32,5.34], respectively. Half-step traces narrow these to [28.51,28.52], [4.72,4.73], and [5.32,5.33]. All three terminal outcomes remain right-basin observations.

The accounting residual is at most approximately 2.22e-16. Boundary velocity calculated by implicit differentiation was checked against nearby root evaluations. This supports the coordinate accounting. It does not separate mutually influencing state and landscape through causal interventions, nor authorize a transition. Approval remains outside this instrument.

## Verification and archaeology

20 checks passed. They cover history split integrity; strict observable schemas; exclusion of hidden coordinates and metadata from features; finite inputs; training-only scaling; deterministic prediction; source-import restrictions; both outcomes in both held-out directions; missing/duplicate/invalid prediction rejection; probability/label consistency; pre-impulse separation; reproduction of all three misses; and boundary-motion accounting.

A fixed random sample of 24 test trials was rerun at dt=.01. There were no terminal-label changes, with maximum end-position difference approximately 1.08e-12. These are sample checks, not uniform error bounds. Diagnostic traces were also checked at half step.

After the first run, inspection added a scoring rejection for disagreement between a predicted label and its own probability vector, plus explicit tests for that condition and hidden-tilt independence of public row construction. No feature, dataset parameter, hyperparameter or prediction rule changed. The full experiment and tests were then rerun. The prediction hash stayed the same. These changes are harness hardening, not improvements to model performance.

## What this earns

Observable inputs can predict many outcomes of this supplied system without handing its equations or hidden tilt to the predictor. In the tested family, current position carries more practically useful information for this learner than the added history representation. Reverse-direction transfer remains weak when that direction is absent from training.

The traces answer one previously unresolved diagnostic question for three specific trajectories. Nothing in this batch establishes that meaningful development creates the topography, that the chosen features constitute a general capacity measure, or that repeated requests can obtain externally authorized impulses. Those claims remain outside the evidence.
