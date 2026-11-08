# Predicting penalty trajectories from the first 0.10 s

[English paper (PDF)](paper/paper.pdf) · [LaTeX source](paper/paper.tex) · [Chinese team handoff](docs/PROJECT_HANDOFF_20261108_ZH.md) · [AI use](AI_USAGE.md) · [Publication scope](docs/publication_notes.md)

[Original full research prompt (Chinese, verbatim)](docs/original_request.txt)

Clone over SSH with `git clone git@github.com:Zephyr-Feng/UPC.git`, then run commands from the cloned repository root.

Detailed team handoff (Chinese, 2026-11-08): [project handoff](docs/PROJECT_HANDOFF_20261108_ZH.md).

Reproducible research project for UPC 2026 Problem B. English manuscript and figures; supplied observations are preserved verbatim in data/supplied_case.json. No real FIFA tracking dataset is used. Synthetic trajectories and camera-noise scenarios are explicitly labeled.

## Reproduce

With the listed scientific Python dependencies available:

```powershell
python -m src.run_all
```

The command runs physical tests, analytical baseline, conditional velocity fitting, 10,000-sample supplied-case uncertainty at four noise scales, paired validation of three models on 1,000 synthetic kicks, a separate mismatch population, observation-duration and aerodynamic sensitivity, figures, manuscript generation, a LaTeX compilation attempt, and the final audit. CPU only; fixed seed 20261107. Runtimes and numerical failures are recorded, not suppressed.

No SHA256 or alternative hash verification is performed. No package installation or system changes are required in the current workspace. Existing NumPy/Matplotlib/pytest are used; PDF fallback uses the bundled ReportLab runtime if unavailable in the main Python environment.

## Read the science

- docs/modeling_notes.md: six dynamic constraints, structural/practical identifiability, analytic noise amplification, boundary events.
- docs/assumptions.md: verified references versus assumed priors and camera errors.
- experiment-plan.md: frozen comparisons, metrics, populations, seed, failure handling and execution ledger.
- docs/competition_requirements.md: official rules, anonymity and AI-output requirement.
- results/: full numerical summaries, raw sample arrays and raw validation rows, including misses and failure classifications.
- figures/: program-generated vector PDF and PNG pairs.
- paper/: English manuscript, LaTeX source, bibliography and rendering/compilation status.
- AI_USAGE.md and docs/original_request.txt: public AI-use statement and exact original research request. Full internal dialogue records are retained locally, not published.

## Interpretation boundaries

The central uncertainty scenario assumes independent 0.01 m coordinate errors and the declared aerodynamic prior. It is not a measured camera specification. Posterior means minimize squared point error; a separate KDE mode describes the most likely location at an explicitly finite resolution. Location intervals condition on an airborne crossing. Goal probability is the chance that the ball center crosses the stated rectangle while airborne, without goalkeeper modeling. Radius clearance is separately reported. Ground-before-goal trajectories are not extrapolated through the ground.

Synthetic validation uses a known simulator and an assumed kick population. A separate changed-lift/changed-drag experiment checks limited model mismatch. Neither establishes real-match accuracy. The weakest scientific element is the aerodynamic prior and simplified lift law, rather than numerical integration precision.

## Human completion before submission

Insert the real TEAM_NUMBER; review all scientific assumptions and the complete AI disclosure, including the exact input and full output required by the rules; check anonymity of any appended chat export; confirm official deadline and registration; submit the actual attachment yourself. No email is sent by this project.

No LaTeX engine was found during preflight. The build records an actual compilation attempt and, if necessary, generates a readable PDF with ReportLab. That fallback is not a successful LaTeX compilation. A full TeX build on a configured system can use `latexmk -pdf paper.tex` from the paper directory.

All scientific bibliography entries are verified against official or author-institution sources listed in docs/assumptions.md. These checks establish reference identity; they do not validate the assumed parameter distributions for a specific tournament ball.

## Computed central result

At the assumed 0.01 m coordinate-noise scale and declared aerodynamic prior, the supplied-kick ensemble mean is (y,z)=(3.08,1.92) m at 0.396 s. The KDE spatial mode is approximately (3.21,1.90) m. Marginal 95% intervals are y=[2.56,3.56] m and z=[1.43,2.43] m; the joint ellipse has semiaxes 0.61 and 0.64 m. The center-point geometric goal probability is 96.5% (radius clearance 91.9%). All are conditional model results.

For 1,000 synthetic kicks, paired RMSE at 1 cm noise is 1.07/0.45/0.41 m for M0/M1/M2 on 836 common coordinate cases. M2 covers 94.6% of 958 airborne true crossings and classifies goal/miss correctly in 89.8% of all 1,000 cases. These are matched-simulator results; the longer-window extension undercovers.

The final scientific paper has 10 pages, a 173-word abstract and seven generated figures. Current PDF renderer: ReportLab fallback; LaTeX compilation unavailable. Review docs/submission_checklist.md before any submission. The raw AI archive is internal and can contain account-identifying local paths.
