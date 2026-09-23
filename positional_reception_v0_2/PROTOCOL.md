# Positional reception v0.2 — protocol set before the first run

2026-09-10. This is an exploratory engineering experiment, not an external preregistration. The inherited substrate is copied byte-for-byte from v0.1. No constitutional or authorization layer is changed.

## Questions and fixed choices

1. Does recent observed position history improve prediction of the terminal basin beyond elapsed time, current position, or both, when landscape coordinates and equations are withheld from the predictor?
2. Does that improvement survive complete-history holdout, separately for forward and reverse histories? An additional forward-only training regime tests transfer to unseen reverse histories.
3. For the three saved v0.1 snapshot misses, how much signed gap change is attributable kinematically to boundary displacement versus state displacement?

Every live step remains dwelling. There is no additional waiting state.

## Dataset

30 training seeds (0–29) and 12 held-out seeds (1000–1011), each generating forward and reverse histories. Each history is entirely assigned to one split. Within each seed, history parameters are sampled once and shared across the two directions, so forward and reverse outcomes are paired, not independent. Phase is uniform [-3.14,3.14], amplitude uniform [0.005,0.035], rate uniform [0.08,0.22], magnitude uniform [0.18,0.31]. The signed target and amplitude preserve bistability. These are variations of the same supplied sinusoidal relaxation family, not new developmental mechanisms.

At times 2, 6, 12 and 24, record x now and at lags 0.5 and 1.0. Apply impulses 0, .3, .45, .6, .75, .9, 1.05, 1.2, 1.35, 1.5 to separate immutable copies. Observe after 24 units of continued dwelling with dt=.02, using the inherited terminal-attractor criterion. Unresolved labels are retained as a third class; they are never silently dropped. Terminal basin is the outcome; an instantaneous moving-boundary encounter is a separate diagnostic.

## Predictors

All models are fixed k=15 nearest-neighbor classifiers with training-only standardization, Euclidean distance, deterministic row-index tie-breaking and empirical neighbor class probabilities. No test-label tuning or hyperparameter search.

- offering: impulse only.
- time: impulse and elapsed time.
- position: impulse and current x.
- time_position: impulse, time and current x.
- history: those same three plus x(now)-x(-.5) and x(-.5)-x(-1).

The intended comparison is history against time_position as well as the simpler baselines. The offering magnitude is known to all predictors. Prediction is conditional on that specified offering; no universal scalar capacity is claimed.

learner.py imports no substrate code. Its strict input schema accepts only observed x samples, elapsed time, impulse, split metadata and training labels. Model features exclude seed, history ID, family, hidden tilt, potential, roots and future samples. The same author constructed both modules; this is an auditable data-access separation, not independent scientific blinding or a hostile-process security boundary. Clean position is still privileged compared with ordinary language observations of an AI.

Predictions are written by a separate process before the evaluator reads held-out labels. Both mixed-direction and forward-only training regimes are fixed before evaluation. Forward/reverse membership selects the training subset in the latter regime, but is never a feature.

## Evaluation and diagnostic traces

Report accuracy, multiclass Brier score (sum over three classes), and unresolved outcomes separately for forward, reverse and combined test sets. Record per-history metrics and paired history-model versus time_position Brier differences; no independence assumption for individual impulse trials and no significance claim. Negative improvements remain results.

Trace the three original v0.1 misses with their actual random.Random(seed) phases. Define g=s(a)-x and preserve pre-impulse, post-impulse and every integration step separately. Signed post-impulse gap closure equals (x-x0) - (s-s0). Also record ds/dt=-da/dt/(1-3s²) and dx/dt. Keep the first sampled sign-change bracket, without claiming exact encounter time. This is a coordinate decomposition, not a causal intervention identifying what alone caused the crossing. The frozen root is not asserted to be the full time-dependent system's invariant basin boundary.

Verify split isolation, training-only normalization, feature allowlisting, schema rejection of hidden fields, outcome-blind test feature construction, deterministic model behavior, trace accounting and the three reproduced misses. A fixed sample of 24 held-out trials and all three diagnostic cases will be checked at half step. No result threshold is used as a passing test of the reception hypothesis.
