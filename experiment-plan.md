# Penalty prediction implementation and experiment plan

Goal: quantify what the first 0.10 s identifies, with a runnable, evidence-bound English report.
Architecture: analytical baseline; shared numerical simulator and conditional state fitting; likelihood-weighted nuisance ensemble; saved raw results drive all figures and manuscript tables.
Tech stack: Python, NumPy, SciPy when available, Matplotlib, pytest. Use existing runtime packages before installing anything. No hash checks.
Spec: docs/original_request.txt (verbatim user request).

## Frozen scientific contract

- Question/hypothesis: does constraining acceleration through physics reduce noisy extrapolation error? No model is presumed to win.
- Claim boundary/story: synthetic performance conditional on a stated population; no real FIFA tracking dataset and no measured spin claim.
- Literature: official UPC/IFAB; verified primary soccer aerodynamic studies. Priors are assumptions even when literature motivates their scale.
- Controls: Model 0 six-parameter effective acceleration; Model 1 fixed-Cd nonspinning three-velocity least squares; Model 2 nuisance-marginalized physics prediction.
- Main table: method, noise (m), N, mean/median/95th error (m), coordinate MAE (m), radial RMSE (m), failures, geometric classification accuracy, 95% region coverage, elapsed cost per case. Missing values are null, never zero.
- Primary metric: root mean squared Euclidean goal-plane error over common physically airborne, successfully predicted cases; also retain counts and all failure rows. Secondary median, tail, classification, coverage, and ground/no-crossing detection.
- Pilot: exact constant velocity/projectile, drag work sign, Magnus cross-product direction, intersection roots, synthetic state recovery, quadrature/Monte Carlo stability.
- Success gate: physical and numerical tests pass; event errors converge under step/tolerance refinement; pilot fits recover known positions; then full runs.
- Expected signal: noise may strongly amplify unconstrained acceleration; complex priors may introduce bias. Either outcome is publishable with evidence.
- Failure modes: likelihood degeneracy, low effective sample size, simulator mismatch, boundary contact, undercoverage, prior dominance, biased omission of misses.
- Main validation: 1,000 independently drawn kicks at four noise levels; fixed seed, paired observations across methods. Include goal and miss cases without outcome selection.
- Uncertainty: 10,000 resamples/particles; compare N=1,000/5,000/10,000; measurement-only, aerodynamic-only, combined scenarios. Monte Carlo error accompanies probabilities.
- Sensitivity: sigma; speed, azimuth/elevation, Cd, spin magnitude/axis, density, lift-law scale; observation windows ending at 0.05/0.10/0.15/0.20 s, always two nonzero observation times at T/2 and T. Extension is labeled.
- Diagnostic robustness: mismatch experiment changes the lift law and drag speed dependence; distinguish matched-model calibration from external validity.
- Resource/seed: local CPU only; seed 20261107; use vectorized batches and bounded processes. No paid APIs, GPU, system changes, or uploads.
- Ownership: primary agent owns implementation and final acceptance; independent reviewer at final gate only if available under applicable workflow.
- Acceptance: report winners from the frozen primary metric without choosing after outcome; report failures, coverage limitations, and prior sensitivity.

## File scope and execution checklist

- [x] Data/requirements/AI log and mathematical identifiability analysis before code.
- [x] tests/test_models.py: analytical roots, ballistic limits, force signs, ground events, numerical convergence, fitting recovery and posterior checks; run failing tests first.
- [x] src/models.py: baseline, physical RHS, observation simulation, event intersection, conditional velocity least squares.
- [x] src/inference.py: explicit priors, likelihood weighting, conditional velocity samples, summaries and region definition.
- [x] src/experiments.py and src/run_all.py: supplied case, uncertainty, convergence, paired synthetic validation, sensitivity, raw CSV/NPZ/JSON, run metadata.
- [x] src/plotting.py: English vector PDF and PNG figures directly from saved results.
- [x] paper/paper.tex and references.bib AFTER all experimental gates; generated numerical macros/tables; abstract last.
- [x] Final audit, actual LaTeX compilation attempt, visual inspection, truthful README and AI disclosure status.

Review focus: ground before goal; missing/decelerating crossings; posterior collapse; noisy observations before x=goal; no initial contact misclassification; dataset population and mismatch claims; manuscript/result consistency.

## Execution ledger

2026-11-07: Empty workspace, no Git repository; therefore no commits or new worktree. User explicitly requested autonomous execution, so no design approval round. Python 3.14 has NumPy and Matplotlib; checking bundled scientific runtime before dependency decisions. All four measurement-noise values are assumptions. Full transcript requirement must not be replaced by a short AI acknowledgment.

2026-11-07 final ledger: all numerical stages executed (567.6 s for main study). Independent review identified latent missing-region coverage, particle-failure aggregation and tangent-launch bugs; regression tests were added and all fixes passed. Existing matched raw rows had no affected cases; content checks confirmed unchanged principal results. All 40 ESS<30 main-population cases were refined to 10,000 particles as a diagnostic, without selecting by error or replacing the frozen comparison. Maximum point-mean change was 0.113 m. Extended-window low ESS and 90.4% coverage remain explicitly reported limitations. PDF image clipping was caught by visual QA and repaired, with a page-boundary regression test. No LaTeX compiler is installed: actual invocation failed, and the readable PDF uses ReportLab. Raw AI-output archive may identify local paths and requires anonymity review; TEAM_NUMBER is still unknown.
