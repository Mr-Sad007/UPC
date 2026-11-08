# Final audit

- PASS: Original observations preserved: Content comparison to official problem coordinates; no checksum.
- PASS: Goal geometry preserved: Ball-center target, separate radius clearance.
- PASS: Complete paired validation: 1000 kicks per noise level; all three methods retained.
- PASS: Independent RMSE M0 sigma=0.005: Recomputed directly from raw predicted and true coordinates.
- PASS: All-case classification M0 sigma=0.005: Includes physical misses and ground-before-goal cases.
- PASS: Independent RMSE M1 sigma=0.005: Recomputed directly from raw predicted and true coordinates.
- PASS: All-case classification M1 sigma=0.005: Includes physical misses and ground-before-goal cases.
- PASS: Independent RMSE M2 sigma=0.005: Recomputed directly from raw predicted and true coordinates.
- PASS: All-case classification M2 sigma=0.005: Includes physical misses and ground-before-goal cases.
- PASS: Independent RMSE M0 sigma=0.01: Recomputed directly from raw predicted and true coordinates.
- PASS: All-case classification M0 sigma=0.01: Includes physical misses and ground-before-goal cases.
- PASS: Independent RMSE M1 sigma=0.01: Recomputed directly from raw predicted and true coordinates.
- PASS: All-case classification M1 sigma=0.01: Includes physical misses and ground-before-goal cases.
- PASS: Independent RMSE M2 sigma=0.01: Recomputed directly from raw predicted and true coordinates.
- PASS: All-case classification M2 sigma=0.01: Includes physical misses and ground-before-goal cases.
- PASS: Independent RMSE M0 sigma=0.02: Recomputed directly from raw predicted and true coordinates.
- PASS: All-case classification M0 sigma=0.02: Includes physical misses and ground-before-goal cases.
- PASS: Independent RMSE M1 sigma=0.02: Recomputed directly from raw predicted and true coordinates.
- PASS: All-case classification M1 sigma=0.02: Includes physical misses and ground-before-goal cases.
- PASS: Independent RMSE M2 sigma=0.02: Recomputed directly from raw predicted and true coordinates.
- PASS: All-case classification M2 sigma=0.02: Includes physical misses and ground-before-goal cases.
- PASS: Independent RMSE M0 sigma=0.05: Recomputed directly from raw predicted and true coordinates.
- PASS: All-case classification M0 sigma=0.05: Includes physical misses and ground-before-goal cases.
- PASS: Independent RMSE M1 sigma=0.05: Recomputed directly from raw predicted and true coordinates.
- PASS: All-case classification M1 sigma=0.05: Includes physical misses and ground-before-goal cases.
- PASS: Independent RMSE M2 sigma=0.05: Recomputed directly from raw predicted and true coordinates.
- PASS: All-case classification M2 sigma=0.05: Includes physical misses and ground-before-goal cases.
- PASS: Normalized weights: Complete central ensemble.
- PASS: Independent geometric probability: In-goal mass includes every particle; no outcome rejection.
- PASS: Independent predictive mean: Conditional on airborne goal-plane intersection.
- PASS: Empirical 95% content: Posterior content checked separately from synthetic frequentist coverage.
- PASS: Abstract limit: 173 words; limit 300.
- PASS: Manuscript result trace: Generated article and TeX use the accepted saved numeric records.
- PASS: Anonymity scaffold: Local home-directory path absent; personal and institution identifiers still require manual review.
- PASS: AI query retained verbatim: Exact user project request preserved, including original line breaks.
- PASS: References verified: Six official or author-institution records; no unverified DOI inserted.
- PASS: Programmatic figure labels: Every visible coordinate axis has a variable/quantity and unit or dimensionless marker.
- PASS: PDF actually generated: Renderer recorded; PDF presence is not claimed as LaTeX compilation.

LaTeX compiled: False. Renderer: ReportLab fallback.

Submission-ready: no. TEAM_NUMBER and the complete AI-output appendix need human review.

## Requested A-T checklist

| Item | Status | Evidence or remaining action |
|---|---|---|
| A | PASS | Original positions and goal dimensions preserved. |
| B | PASS | Reported numerical results come from executed calculations. |
| C | PASS | Complete python -m src.run_all execution returned exit code 0. |
| D | PASS | Seven figure pairs generated programmatically. |
| E | PASS | Coordinate axes have units; category axes are explicitly categorical. |
| F | PASS | Core manuscript quantities trace to saved numerical records. |
| G | PASS | No fabricated citation identified; six source identities verified. |
| H | PASS | No unverified bibliography entry retained. |
| I | PASS | SI-unit equations and force-direction/ballistic tests checked. |
| J | PASS | Aerodynamic, measurement and synthetic-population assumptions declared. |
| K | PASS | Six scalar constraints and aerodynamic non-identifiability explicitly analyzed. |
| L | PASS | General-method synthetic validation, misses and mismatch test performed. |
| M | PASS | Measurement, nuisance and combined uncertainty quantified. |
| N | PASS | Physical no-point rates, numerical-failure mass and undercoverage retained. |
| O | CONDITIONAL | Science paper anonymity checked; raw AI archive still needs anonymity review. |
| P | PASS | Abstract is 173 words, below 300. |
| Q | OPEN | AI disclosure section and exact internal archive exist; full closing appendix requires team review. |
| R | OPEN | TEAM_NUMBER deliberately remains until the actual team number is supplied. |
| S | PASS | No student/institution identity inserted into the scientific manuscript. |
| T | PASS | Manuscript uses appropriately rounded values; raw machine records keep calculation precision. |
