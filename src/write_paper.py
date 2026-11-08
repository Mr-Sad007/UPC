"""Evidence-bound manuscript: one structured source for TeX and readable PDF."""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .experiments import ROOT, RESULTS, save_csv, clean
from .convergence import load_rows

PAPER = ROOT/'paper'


def tex_escape(text):
    pieces = re.split(r'(\\cite\{[^}]+\})', text)
    mapping = {'&': r'\&', '%': r'\%', '#': r'\#', '_': r'\_', '$': r'\$',
               '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
    return ''.join(p if p.startswith('\\cite{') else ''.join(mapping.get(c, c) for c in p) for p in pieces)


def write_paper():
    PAPER.mkdir(exist_ok=True)
    (PAPER/'assets').mkdir(exist_ok=True)
    supplied = json.loads((RESULTS/'supplied_case.json').read_text())
    manifest = json.loads((RESULTS/'run_manifest.json').read_text())
    metrics = load_rows('validation_metrics.csv')
    mismatch = load_rows('mismatch_metrics.csv')
    durations = load_rows('duration_metrics.csv')
    priors = load_rows('prior_sensitivity.csv')
    convergence = load_rows('monte_carlo_convergence.csv')
    particle = load_rows('particle_convergence.csv')
    numerical = load_rows('numerical_convergence.csv')
    s = supplied['sigma_0.01_m']['M2']
    mode = supplied['M2_kde_mode']
    central = {r['model']: r for r in metrics if r['sigma_m'] == .01}
    end = {r['model']: r for r in durations if r['population'] == 'extended_T_0.2'}
    start = {r['model']: r for r in durations if r['population'] == 'extended_T_0.05'}
    high = {r['model']: r for r in metrics if r['sigma_m'] == .05}
    mismatch2 = next(r for r in mismatch if r['model'] == 'M2')
    blocks = []
    def section(text): blocks.append(dict(kind='section', text=text))
    def paragraph(text): blocks.append(dict(kind='paragraph', text=text))
    def equation(latex): blocks.append(dict(kind='equation', latex=latex, asset=f'equation_{sum(b["kind"] == "equation" for b in blocks)+1}.png'))
    def figure(name, caption): blocks.append(dict(kind='figure', name=name, caption=caption))
    def table(headers, rows, widths, caption):
        assert abs(sum(widths)-1) < 1e-9
        assert all(len(row) == len(headers) for row in rows)
        blocks.append(dict(kind='table', headers=headers, rows=rows, widths=widths, caption=caption))
    section('1. Problem and information budget')
    paragraph('How much of a penalty trajectory is determined by its first 0.10 s? The target is the first forward crossing of the ball center through x = 11 m. The goal rectangle has -3.66 < y < 3.66 m and 0 < z < 2.44 m. The supplied positions are (0, 0, 0.11), (1.50, 0.45, 0.44), and (2.96, 0.86, 0.74) m at 0, 0.05 and 0.10 s, respectively. These are the official inputs, preserved without adjustment.\\cite{upc2026}')
    paragraph('With the initial position fixed, the later positions provide six scalar dynamical constraints. Initial velocity needs three parameters; unconstrained effective acceleration needs another three. Gravity plus an unknown drag coefficient and three spin components needs at least seven. An independent lift scale would add an eighth and create a spin-scale degeneracy. Thus a full aerodynamic inversion is structurally underdetermined. Counting all nine position coordinates while omitting the known initial state would overstate the information available.')
    paragraph('A dimensionless local sensitivity calculation, scaling the velocity components by (30, 10, 10) m/s, drag by 0.25 and each spin component by 40 rad/s, confirms a six-by-seven matrix of rank six and a nontrivial null direction. These scales describe perturbations, not parameter error bars. The spin component parallel to velocity supplies no initial Magnus force. A unique numerical optimizer output therefore cannot establish a unique spin measurement. Three-dimensional aerodynamic coupling is essential even when its parameters remain uncertain.\\cite{myers2013}')

    section('2. A hierarchy of physical models')
    paragraph('Model 0 is a deliberately unconstrained baseline. For equally spaced observations with h = 0.05 s and displacement vectors d1 and d2 from the initial position, the effective velocity and acceleration are obtained analytically:')
    equation(r'\mathbf{r}(t)=\mathbf{r}_0+\mathbf{v}_0t+\frac{1}{2}\mathbf{a}t^2,\qquad \mathbf{v}_0=\frac{4\mathbf{d}_1-\mathbf{d}_2}{2h},\qquad \mathbf{a}=\frac{\mathbf{d}_2-2\mathbf{d}_1}{h^2}.')
    v, a = supplied['M0']['velocity_m_s'], supplied['M0']['effective_acceleration_m_s2']
    paragraph(f'The supplied data give v0 = ({v[0]:.1f}, {v[1]:.1f}, {v[2]:.1f}) m/s and a = ({a[0]:.0f}, {a[1]:.0f}, {a[2]:.0f}) m/s squared. These are short-window effective accelerations, not constant measured aerodynamic forces. The first forward root is selected; a later returning root is rejected. A negative discriminant or ground contact before the plane is retained as a no-point outcome.')
    equation(r't_g=\frac{2L}{v_{0x}+\sqrt{v_{0x}^2+2a_xL}},\qquad L=11\ {\rm m}.')
    paragraph('Models 1 and 2 use gravity and quadratic drag, with Model 2 additionally including a reduced Magnus term. In the following equations, r and v are position and velocity, omega is a constant angular-velocity vector, m is mass, A is cross-sectional area, rho is air density, R is ball radius, g is gravitational acceleration, and alpha is a fixed lift-law scale:')
    equation(r'\frac{d\mathbf{r}}{dt}=\mathbf{v},\qquad \frac{d\mathbf{v}}{dt}=-g\mathbf{e}_z-k C_D|\mathbf{v}|\mathbf{v}+k\alpha R(\omega\times\mathbf{v}),\qquad k=\frac{\rho A}{2m}.')
    paragraph('Model 1 sets spin to zero and Cd to 0.25, fitting only three velocity components by nonlinear least squares. This isolates a low-variance physical constraint without pretending that drag was measured. Model 2 fixes alpha = 1 and treats drag, density and spin as nuisance parameters. Its linear lift relation is Cl = alpha R |omega|/|v|, with the cross product supplying the sine of the spin-velocity angle. Spin rate and an independent lift coefficient are never fitted simultaneously. Drag always opposes velocity, and the Magnus term performs no instantaneous work.')
    table(['Quantity', 'Value or prior', 'Status'], [
        ['Mass; radius', '0.43 kg; 0.11 m', 'Representative choices within IFAB size/mass limits'],
        ['Area; gravity', 'pi R squared; 9.81 m/s squared', 'Derived geometry; nominal local gravity'],
        ['Density', 'Uniform 1.15-1.30 kg/m cubed', 'Assumed environmental sensitivity range'],
        ['Drag coefficient', 'Uniform 0.12-0.40', 'Assumed range, not ball-specific measurements'],
        ['Spin magnitude; axis', 'Uniform 0-80 rad/s; isotropic', 'Assumed prior, not FIFA population statistics']],
        [.23, .34, .43], 'Parameter provenance. Nominal density is 1.225 kg/m cubed; Model 1 uses nominal density. Every prior is an assumption.')
    paragraph('IFAB permits 410-450 g and circumference 68-70 cm; the selected mass and radius are representative values.\\cite{ifab} Wind-tunnel studies show that drag depends on ball design and flow regime.\\cite{asai2013} Published soccer-flight modeling uses comparable nominal mass, area and air density, but a punt-kick study does not calibrate an unknown penalty ball or our linear lift law.\\cite{linthorne2011} The prior ranges in the table are consequently labeled assumptions, even where their scales are physically motivated.')
    paragraph(f'Flight is integrated with fourth-order Runge-Kutta steps of 0.01 s. Synthetic truth uses 0.0025 s. Cubic Hermite interpolation and 36 bisections locate the first plane crossing or downward ground contact at z = R. Across three numerical probes, the maximum endpoint difference between 0.01 s and 0.00125 s integration was {numerical[1]["max_point_difference_m"]:.1e} m, far below the measurement scenarios. Tests also recover constant velocity and the exact gravity-only parabola, verify force directions, and handle tangent launches with upward acceleration. No bounce is extrapolated through the ground.')

    section('3. Prediction with unresolved aerodynamic parameters')
    paragraph('We assume independent, isotropic Gaussian coordinate noise on the two later positions and exact initial position and times. No camera specification is supplied, so sigma = 0.005, 0.01, 0.02 and 0.05 m are sensitivity scenarios. A central scenario of 0.01 m is used for detailed interpretation. These scales are not inferred from the residuals of six observations.')
    equation(r'p(\mathbf{y}\mid\mathbf{v}_0,\eta,\sigma)\ \propto\ \exp\left[-\frac{\sum_{j=1}^2|\mathbf{r}(t_j;\mathbf{v}_0,\eta)-\mathbf{y}_j|^2}{2\sigma^2}\right].')
    paragraph('For each prior draw of nuisance parameters eta = (Cd, rho, omega), we minimize the six-coordinate squared residual over the three initial-velocity components. A broad, locally constant velocity prior has each component in [-60, 60] m/s and positive forward velocity. The conditional velocity posterior is integrated by a local Laplace approximation, rather than setting the fitted velocity to an exactly known value. If J is the six-by-three position Jacobian with respect to velocity, prior importance weights are:')
    equation(r'w_i\ \propto\ \frac{\exp[-S_i/(2\sigma^2)]}{\sqrt{\det(J_i^{T}J_i)}},\qquad \sum_i w_i=1,\qquad N_{\rm eff}=\frac{1}{\sum_i w_i^2}.')
    paragraph('S_i is the minimized residual sum of squares. Constants common to nuisance draws cancel. For each draw, we perturb the two observed positions with the assumed Gaussian noise, refit velocity conditionally, and propagate to the first event. This perturb-and-refit step approximates the local conditional state distribution; it is not a second likelihood update. We retain prior-averaged nuisance uncertainty and conditional state uncertainty together. Measurement-only propagation fixes representative nuisance parameters; nuisance-only propagation fixes the observed positions while retaining their likelihood. Those decompositions are conditional experiments, not additive causal variance components.')
    paragraph('The posterior mean is the point estimate used for squared-error comparison. The most likely location is reported separately as a Gaussian-KDE grid mode, with Scott bandwidth scaling and stated grid resolution. Means, medians, covariance, marginal quantiles, event probabilities and effective sample sizes are saved. For a joint region, q95 is the weighted empirical 95th percentile of squared Mahalanobis distance, avoiding an untested Gaussian 5.99 threshold:')
    equation(r'{\cal E}_{.95}=\{\mathbf{q}:(\mathbf{q}-\mu)^T\Sigma^{-1}(\mathbf{q}-\mu)\leq q_{.95}\},\qquad \mathbf{q}=(y_g,z_g).')
    paragraph('Location statistics condition on airborne plane crossing. Probability mass assigned to ground contact, no forward crossing or numerical failure is retained separately. Geometric goal probability uses the stated center-point rectangle; radius clearance instead uses |y| < 3.55 m and 0.11 < z < 2.33 m. Neither includes a goalkeeper, posts, net interaction, or rule-complete goal adjudication.')

    section('4. General-method validation')
    paragraph(f'The main population contains {manifest["n_validation"]} independently generated kicks: speed uniformly 22-35 m/s, azimuth uniformly -22 to 22 degrees, elevation uniformly 5-18 degrees, and the stated nuisance distributions. These are synthetic design choices. The forward simulator generates full trajectories, but each estimator receives only the initial position and two noisy early positions. No future endpoint, true velocity, spin, drag or goal label enters inference. Methods use paired noisy observations; noise is scaled from the same standardized draws across the four noise scenarios. The fixed seed is {manifest["seed"]}.')
    paragraph(f'There are {central["M2"]["n_true_crossings"]:.0f} airborne true crossings and {central["M2"]["n_cases"]-central["M2"]["n_true_crossings"]:.0f} ground-before-plane cases, all retained. Error is Euclidean distance in the y-z plane. We report coordinate MAE, radial RMSE, median and 95th-percentile error, physical no-point rate, numerical failure rate, geometric goal/miss accuracy, and region coverage. Paired RMSE uses cases where all three methods supply coordinates; no-point rates prevent hiding excluded failures. Classification uses every generated case, assigning ground-before-goal as a miss. An unavailable region on an airborne truth counts as uncovered.')
    equation(r'E=\sqrt{(y_{\rm pred}-y_{\rm true})^2+(z_{\rm pred}-z_{\rm true})^2},\qquad {\rm RMSE}=\sqrt{\frac{1}{n}\sum_{i=1}^n E_i^2}.')
    paragraph(f'The main validation uses {manifest["posterior_particles_per_validation_case"]} nuisance particles per case; supplied-case uncertainty uses {manifest["supplied_mc_samples"]:,}. A separate {manifest["n_validation"]}-kick mismatch experiment saturates the linear lift response by dividing it by sqrt(1 + (spin ratio/0.25) squared), and changes drag by a speed-dependent factor 1 + 0.2 tanh((25 - speed)/5), with speed in m/s. These are declared stress-test laws, not independently measured aerodynamics. Matched-simulator validation checks internal calibration; the mismatch test checks only these two departures.')

    section('5. Accuracy, failures and calibration')
    rows = []
    for model in ['M0', 'M1', 'M2']:
        r = central[model]
        rows.append([model, f'{r["common_mean_error_m"]:.2f}', f'{r["common_median_error_m"]:.2f}',
                     f'{r["common_p95_error_m"]:.2f}', f'{r["common_rmse_m"]:.2f}',
                     f'{100*r["no_point_rate_on_true_crossings"]:.1f}', f'{1000*r["elapsed_s_per_case"]:.2g}'])
    table(['Model', 'Mean (m)', 'Median (m)', '95th (m)', 'RMSE (m)', 'No point (%)', 'Cost (ms)'], rows,
          [.10, .14, .15, .14, .14, .18, .15],
          f'At sigma = 0.01 m. All four error columns use the same {central["M2"]["n_common"]:.0f} common cases. No-point rate uses all {central["M2"]["n_true_crossings"]:.0f} airborne truths. Cost is measured batched CPU elapsed time per case, excluding generation of truth; it is not an optimized deployment benchmark.')
    improvement = 100*(1-central['M2']['common_rmse_m']/central['M1']['common_rmse_m'])
    paragraph(f'Model 2 has the lowest paired RMSE in the four tested noise scenarios; at 1 cm, its reduction relative to Model 1 is {improvement:.0f}%. Its model-specific median error is {central["M2"]["median_error_m"]:.2f} m and its 95th-percentile error is {central["M2"]["p95_error_m"]:.2f} m. The coordinate MAEs are {central["M2"]["mae_y_m"]:.2f} m in y and {central["M2"]["mae_z_m"]:.2f} m in z. Goal/miss classification is {100*central["M2"]["classification_accuracy"]:.1f}% over all kicks, versus {100*central["M1"]["classification_accuracy"]:.1f}% for fixed drag and {100*central["M0"]["classification_accuracy"]:.1f}% for the baseline.')
    paragraph(f'The nominal 95% ellipse covers {100*central["M2"]["coverage_95"]:.1f}% of {central["M2"]["coverage_n"]:.0f} airborne truths at 1 cm. This is a measured calibration result, not an assumed 95% guarantee. No numerical particle failure was observed in the tested main population. Physical no-point outcomes are substantial for unconstrained acceleration and remain in the raw tables. At 5 cm the paired RMSEs are {high["M1"]["common_rmse_m"]:.3f} m for fixed drag and {high["M2"]["common_rmse_m"]:.3f} m for Model 2: this small descriptive difference does not establish a meaningful practical advantage, and classification is essentially tied.')
    figure('validation', 'Paired synthetic errors at sigma = 0.01 m (left), and predicted versus true coordinates for Model 2 (right). Only common airborne coordinate cases enter this display; failure and classification denominators are reported separately.')
    figure('measurement_noise', 'Noise dependence in the main synthetic population. Left: RMSE on common coordinate cases within each scenario, whose sample count changes with noise. Right: the proportion of airborne truths receiving no plane-coordinate prediction. No-point events include physically predicted ground contact and are distinct from numerical failures.')
    paragraph(f'The mismatch population gives Model 2 paired RMSE {mismatch2["common_rmse_m"]:.2f} m and coverage {100*mismatch2["coverage_95"]:.1f}%. Lift saturation makes this particular population less strongly curved; therefore its smaller error is not evidence of general robustness. Coverage well above 95% indicates conservative regions under this changed law. Unmodeled winds, drag crises and unsteady side forces could produce different errors.')

    section('6. Prediction for the supplied kick')
    rows = [[m, f'{supplied[m]["time_s"]:.3f}', f'{supplied[m]["point_m"][1]:.2f}', f'{supplied[m]["point_m"][2]:.2f}'] for m in ['M0', 'M1']]
    rows.append(['M2 mean', f'{s["mean_crossing_time_s"]:.3f}', f'{s["mean_yz_m"][0]:.2f}', f'{s["mean_yz_m"][1]:.2f}'])
    rows.append(['M2 KDE mode', 'Not a joint time mode', f'{mode["mode_yz_m"][0]:.2f}', f'{mode["mode_yz_m"][1]:.2f}'])
    table(['Model', 'Crossing time (s)', 'y (m)', 'z (m)'], rows, [.28, .32, .20, .20],
          'Deterministic M0/M1 intersections and Model 2 conditional posterior summaries at sigma = 0.01 m. A pointwise spatial mode is not assigned an invented most likely crossing time.')
    paragraph(f'The most likely spatial location is approximately ({mode["mode_yz_m"][0]:.2f}, {mode["mode_yz_m"][1]:.2f}) m under the central scenario, while the squared-error-optimal posterior mean is ({s["mean_yz_m"][0]:.2f}, {s["mean_yz_m"][1]:.2f}) m. The KDE grid spacing is approximately {100*mode["grid_spacing_yz_m"][0]:.0f} cm in each direction, so its peak should not be interpreted more precisely. Mean crossing time is {s["mean_crossing_time_s"]:.3f} s, with a 95% interval of {s["crossing_time_95_s"][0]:.3f}-{s["crossing_time_95_s"][1]:.3f} s.')
    paragraph(f'The marginal 95% intervals are y = [{s["marginal_95_yz_m"][0][0]:.2f}, {s["marginal_95_yz_m"][0][1]:.2f}] m and z = [{s["marginal_95_yz_m"][1][0]:.2f}, {s["marginal_95_yz_m"][1][1]:.2f}] m. The joint 95% ellipse has semiaxes {s["ellipse_semiaxes_m"][0]:.2f} and {s["ellipse_semiaxes_m"][1]:.2f} m; the two marginal intervals do not themselves form a joint 95% rectangle. The covariance matrix, in square meters, is:')
    cov = s['covariance_m2']
    equation(r'\Sigma=\left(\begin{array}{cc}'+f'{cov[0][0]:.4f} & {cov[0][1]:.4f}'+r'\\'+f'{cov[1][0]:.4f} & {cov[1][1]:.4f}'+r'\end{array}\right)\ {\rm m}^2.')
    paragraph(f'The center-point in-goal probability is {100*s["goal_probability"]:.1f}%, and radius-clearance probability is {100*s["radius_clearance_probability"]:.1f}%. Their difference matters because the region approaches the crossbar and side boundary. The Monte Carlo standard error of the first probability is approximately {100*s["goal_probability_mc_se"]:.2f} percentage points; it does not include prior or physical-model error. Effective sample size is {s["ess"]:.0f} of {s["n"]:,}, with no noncrossing or numerical-failure mass in this scenario.')
    figure('trajectory', 'Supplied observations and extrapolations. Model 2 displays a trajectory using representative posterior nuisance parameters, rather than claiming that a trajectory through posterior means is itself the mean trajectory. The rectangle lies in the goal plane.')
    figure('goal_plane', 'Supplied-kick predictive distribution at sigma = 0.01 m. The cloud is a weighted resample for display; the ellipse is computed from the complete ensemble. The star denotes the KDE spatial mode, the cross the posterior mean. Portions outside the rectangle retain their miss probability.')

    section('7. Sensitivity, convergence and observation duration')
    components = supplied['uncertainty_components']
    paragraph(f'With representative nuisance parameters fixed, coordinate standard deviations from measurement noise alone are {components["measurement_only"]["std_yz_m"][0]:.3f} and {components["measurement_only"]["std_yz_m"][1]:.3f} m. With observations fixed, nuisance spread gives {components["aerodynamic_only"]["std_yz_m"][0]:.2f} and {components["aerodynamic_only"]["std_yz_m"][1]:.2f} m. Combined values are {s["std_yz_m"][0]:.2f} and {s["std_yz_m"][1]:.2f} m. Thus unresolved aerodynamics dominate this conditional scenario; the two components are not guaranteed to add exactly.')
    paragraph(f'Changing only the assumed spin ceiling from {priors[0]["spin_max_rad_s"]:.0f} to {priors[2]["spin_max_rad_s"]:.0f} rad/s moves the supplied mean y from {priors[0]["mean_y_m"]:.2f} to {priors[2]["mean_y_m"]:.2f} m and the geometric goal probability from {100*priors[0]["goal_probability"]:.1f}% to {100*priors[2]["goal_probability"]:.1f}%. These are alternative priors, not competing measurements. Conditional sweeps of drag, density, spin rate, spin axis and lift scale, and population-bin analyses of speed and launch directions, are saved. Velocity perturbations are propagated separately to quantify how initial y/z motion affects the remote endpoint.')
    figure('uncertainty_components', 'Left: conditional uncertainty components; the bars are not an additive variance decomposition. Right: alternative prior scenarios with mean plus/minus one standard deviation, rather than 95% error bars. The final scenario widens the drag prior as well.')
    figure('aerodynamic_sensitivity', 'Endpoint sensitivity with the supplied observations held fixed and initial velocity refitted for each nuisance value. Right: a 50 rad/s spin vector rotates in the y-z plane. These are conditional model responses, not identified physical parameters.')
    paragraph(f'Increasing supplied-case sampling from {int(convergence[0]["N"]):,} through {int(convergence[1]["N"]):,} to {int(convergence[2]["N"]):,} changes the reported mean y from {convergence[0]["mean_y_m"]:.3f} to {convergence[1]["mean_y_m"]:.3f} to {convergence[2]["mean_y_m"]:.3f} m. Mean z remains approximately {convergence[-1]["mean_z_m"]:.2f} m. The goal-probability range across these sample sizes is {100*min(r["goal_probability"] for r in convergence):.2f}-{100*max(r["goal_probability"] for r in convergence):.2f}%. This supports centimeter-scale stability of the central mean, not exact probability convergence.')
    paragraph(f'In the 5 mm main-validation scenario, {len(particle)} cases have effective sample size below 30 with the frozen 512-particle budget. Refining every such case to 10,000 particles changes the mean coordinate prediction by at most {max(r["point_change_m"] for r in particle):.2f} m; these diagnostic results are preserved separately and the frozen main comparison is unchanged. Low effective sample size is a computational limitation, not evidence of a precisely known spin.')
    paragraph(f'The extended analysis uses {manifest["duration_generated_cases"]} additional kicks and only two later observations at T/2 and T, with sigma = 0.01 m. It does not add observations to the original problem. Common-case Model 2 RMSE decreases from {start["M2"]["common_rmse_m"]:.2f} m at T = 0.05 s to {end["M2"]["common_rmse_m"]:.2f} m at T = 0.20 s. At 0.20 s, constant acceleration gives {end["M0"]["common_rmse_m"]:.2f} m, better than the fixed-drag model at {end["M1"]["common_rmse_m"]:.2f} m. This demonstrates that adding a physical constraint can increase prediction error when spin is omitted; RMSE alone does not separate bias and variance.')
    figure('observation_duration', 'Extended two-observation experiment, independent of the official supplied data. Common coordinate-case sets vary with duration. Longer observation improves these mean errors; it does not by itself validate goalkeeper reaction decisions or calibrated uncertainty.')
    paragraph(f'The extension uses 256 particles per case. At T = 0.20 s its nominal 95% ellipse covers only {100*end["M2"]["coverage_95"]:.1f}% of airborne truths, and the minimum effective sample size is {end["M2"]["minimum_ess"]:.1f}. Narrower likelihoods challenge direct prior importance sampling. This undercoverage is retained as a failed calibration check; the extended results cannot justify a universal observation-time threshold for reliable goalkeeping. More efficient posterior sampling or substantially more particles would be needed before such a claim.')

    section('8. Physical interpretation, strengths and limitations')
    paragraph('The baseline differentiates noisy coordinates twice. At fixed extrapolation time t, the coefficients of the two noisy positions are c1 = 2t/h - (t/h) squared and c2 = ((t/h) squared - t/h)/2. Coordinate uncertainty is therefore sigma sqrt(c1 squared + c2 squared), before accounting for uncertain crossing time. Acceleration noise grows as sqrt(5) sigma/h squared. This explains its steep noise sensitivity: effective curvature that exactly interpolates early positions is a noisy quantity, and exact interpolation supplies no residual check.')
    paragraph('The physical models reduce this variance by restricting acceleration directions and magnitudes. Their gain depends on whether those restrictions describe the kick. Fixed drag cannot reproduce all sideways curvature, while an ensemble allows several nearly indistinguishable early trajectories to diverge by the goal. More physical free parameters would not create more observations. Averaging over unresolved parameters is a conditional uncertainty calculation, not a successful measurement of them.')
    paragraph('Strengths are an explicit information budget, analytic baseline, physically signed forces, first-event root finding, retained misses and failures, paired general-method validation, uncertainty calibration tests, and numerical traceability. Every displayed numerical result and figure is generated from saved calculations. The single-command pipeline records its environment and uses no remote paid computation.')
    paragraph('The dominant scientific limitation is the unmeasured aerodynamic prior and assumed lift law. The supplied ball, atmosphere, spin, tracking error and timing precision are unknown. Wind, spin decay, ball deformation, unsteady wake effects, drag crisis, camera bias and correlated errors are omitted. Initial position is treated as exact. Synthetic validation shares its main equations with inference, and the limited mismatch test is not field validation. The Laplace velocity approximation and low effective sample sizes limit some uncertainty estimates. No method here predicts goalkeeper motion or actual save probability. More trajectory points, calibrated cameras, measured spin and velocity, and independent flight tracks would reduce different parts of this uncertainty.')

    section('9. Conclusion')
    paragraph(f'Two later positions constrain motion trends but do not uniquely recover drag and a spin vector. A conditional aerodynamic ensemble achieves paired RMSE {central["M2"]["common_rmse_m"]:.2f} m and {100*central["M2"]["coverage_95"]:.1f}% nominal-95% coverage in the stated 1 cm synthetic scenario. For the supplied kick, the central-prior mean is ({s["mean_yz_m"][0]:.2f}, {s["mean_yz_m"][1]:.2f}) m at {s["mean_crossing_time_s"]:.3f} s; the KDE spatial mode is approximately ({mode["mode_yz_m"][0]:.2f}, {mode["mode_yz_m"][1]:.2f}) m. The joint uncertainty spans roughly six-tenths of a meter in each principal direction. This conditional distribution, together with its prior dependence and calibration limitations, is more defensible than a purported unique spin reconstruction.')

    references = [
        dict(key='upc2026', text='University Physics Competition. 2026 Competition, Problem B: Predicting FIFA Penalty Trajectories. https://university-physics-competition.com/2026-competition (accessed 7 November 2026).', url='https://university-physics-competition.com/2026-competition'),
        dict(key='myers2013', text='T. G. Myers and S. L. Mitchell. A mathematical analysis of the motion of an in-flight soccer ball. Sports Engineering 16(1), 29-41 (2013). DOI: 10.1007/s12283-012-0105-8.', url='https://pure.ul.ie/en/publications/a-mathematical-analysis-of-the-motion-of-an-in-flight-soccer-ball/'),
        dict(key='ifab', text='The International Football Association Board. Laws of the Game, Law 2: The Ball. https://www.theifab.com/laws/latest/the-ball/ (accessed 7 November 2026).', url='https://www.theifab.com/laws/latest/the-ball/'),
        dict(key='asai2013', text='T. Asai and K. Seo. Aerodynamic drag of modern soccer balls. SpringerPlus 2, 171 (2013). DOI: 10.1186/2193-1801-2-171.', url='https://tsukuba.repo.nii.ac.jp/records/29043'),
        dict(key='linthorne2011', text='N. P. Linthorne and D. S. Patel. Optimum Projection Angle for Attaining Maximum Distance in a Soccer Punt Kick. Journal of Sports Science and Medicine 10(1), 203-214 (2011). https://pmc.ncbi.nlm.nih.gov/articles/PMC3737918/.', url='https://pmc.ncbi.nlm.nih.gov/articles/PMC3737918/'),
        dict(key='upcrules', text='University Physics Competition. Contest Rules, rules 5-6. https://uphysicsc.com/contestrules.html (accessed 7 November 2026).', url='https://uphysicsc.com/contestrules.html')]
    ai_report = [
        'OpenAI Codex was used for source lookup, modeling analysis, scientific programming, numerical experiments, plotting, English drafting and artifact checks. The exact underlying model identifier is not asserted. The scientific claims are limited to executed calculations and explicitly declared assumptions.',
        'The official rules require the exact query and the complete AI output, in addition to naming the system.\\cite{upcrules} The original project query is preserved verbatim in AI_LOG.md and docs/original_request.txt. Generated source files, numerical outputs and a visible-output archive document the assistance. This current research draft does not assert that a concise acknowledgment substitutes for the full required transcript. The complete exact input/output appendix must be reviewed and appended before contest submission. TEAM_NUMBER remains a deliberate placeholder.']
    # Abstract is written last, after all result-bearing manuscript blocks.
    abstract = (f'Predicting a penalty kick from only two positions after launch is an inverse problem with six dynamical constraints. '
                f'We compare analytic constant-acceleration extrapolation, a gravity-plus-drag fit, and an aerodynamic ensemble that marginalizes unresolved drag, density and spin. '
                f'Independent Gaussian coordinate errors are sensitivity assumptions, not measured camera specifications. '
                f'In {manifest["n_validation"]} synthetic kicks observed through 0.10 s with 0.01 m coordinate noise, paired goal-plane RMSEs are '
                f'{central["M0"]["common_rmse_m"]:.2f}, {central["M1"]["common_rmse_m"]:.2f} and {central["M2"]["common_rmse_m"]:.2f} m, respectively; '
                f'the ensemble nominal 95% ellipse covers {100*central["M2"]["coverage_95"]:.1f}% of airborne truths. '
                f'For the supplied kick, the conditional ensemble mean is (y, z) = ({s["mean_yz_m"][0]:.2f}, {s["mean_yz_m"][1]:.2f}) m at {s["mean_crossing_time_s"]:.3f} s, '
                f'and the most likely spatial location is approximately ({mode["mode_yz_m"][0]:.2f}, {mode["mode_yz_m"][1]:.2f}) m. '
                f'The joint 95% ellipse has semiaxes {s["ellipse_semiaxes_m"][0]:.2f} and {s["ellipse_semiaxes_m"][1]:.2f} m; geometric center-point goal probability is {100*s["goal_probability"]:.1f}% under the stated prior. '
                'Unknown aerodynamics dominate conditional position noise. Longer observation reduces point error in an extended experiment, while undercoverage accompanies low effective sample sizes. '
                'Short observations support conditional probabilistic predictions rather than unique spin recovery; independent aerodynamic and tracking measurements remain necessary for field calibration.')
    assert len(abstract.split()) <= 300
    article = dict(title='What the First 0.10 Seconds Reveal About a Penalty Kick', abstract=abstract,
                   abstract_word_count=len(abstract.split()), blocks=blocks, references=references, ai_report=ai_report)
    (PAPER/'article.json').write_text(json.dumps(clean(article), indent=2), encoding='utf-8')
    render_equations(blocks)
    render_tex(article)
    write_bibliography()
    save_csv('citation_verification.csv', [dict(key=r['key'], status='VERIFIED_IDENTITY', checked_date='2026-11-07',
                                               owning_source=r['url'], caveat='Does not validate assumed priors') for r in references])
    trace = dict(supplied_case_source='results/supplied_case.json', validation_source='results/validation_metrics.csv',
                 mismatch_source='results/mismatch_metrics.csv', duration_source='results/duration_metrics.csv',
                 uncertainty=s, central_metrics=central, most_likely_mode=mode,
                 abstract_word_count=len(abstract.split()))
    (PAPER/'claim_trace.json').write_text(json.dumps(clean(trace), indent=2), encoding='utf-8')
    print(f'Wrote manuscript, equations, bibliography; abstract {len(abstract.split())} words.', flush=True)


def render_equations(blocks):
    for b in blocks:
        if b['kind'] != 'equation': continue
        latex = b['latex']
        if '\\begin{array}' in latex:
            # MathText has no array environment: preserve the same matrix in a compact two-line asset.
            cov = json.loads((RESULTS/'supplied_case.json').read_text())['sigma_0.01_m']['M2']['covariance_m2']
            latex = (r'\Sigma_{yy}='+f'{cov[0][0]:.4f}'+r',\quad \Sigma_{yz}=\Sigma_{zy}='+f'{cov[0][1]:.4f}'
                     +r',\quad \Sigma_{zz}='+f'{cov[1][1]:.4f}'+r'\quad({\rm m}^2).')
        fig = plt.figure(figsize=(8, .52))
        fig.text(.5, .5, '$'+latex+'$', ha='center', va='center', fontsize=12)
        fig.savefig(PAPER/'assets'/b['asset'], dpi=180, bbox_inches='tight', pad_inches=.10, facecolor='white')
        plt.close(fig)


def render_tex(article):
    lines = [r'\documentclass[11pt,a4paper]{article}',
             r'\usepackage[T1]{fontenc}', r'\usepackage{amsmath,amssymb,graphicx,booktabs,geometry,fancyhdr,hyperref}',
             r'\geometry{margin=0.82in}', r'\hypersetup{hidelinks,pdfauthor={TEAM_NUMBER}}',
             r'\newcommand{\teamnumber}{\detokenize{TEAM_NUMBER}}',
             r'\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\teamnumber}\fancyfoot[R]{\thepage}',
             r'\setlength{\headheight}{14pt}', r'\begin{document}', r'\begin{titlepage}\thispagestyle{fancy}\fancyfoot{}',
             r'\centering\vspace*{0.4in}', r'{\Large Problem B\par}\vspace{0.35in}',
             r'{\LARGE\bfseries '+tex_escape(article['title'])+r'\par}\vspace{0.35in}',
             r'\begin{abstract}', tex_escape(article['abstract']), r'\end{abstract}', r'\end{titlepage}']
    for block in article['blocks']:
        kind = block['kind']
        if kind == 'section':
            title = re.sub(r'^\d+\.\s*', '', block['text'])
            lines.append(r'\section{'+tex_escape(title)+'}')
        elif kind == 'paragraph': lines.extend([tex_escape(block['text']), ''])
        elif kind == 'equation': lines.extend([r'\begin{equation}', block['latex'], r'\end{equation}'])
        elif kind == 'figure':
            lines.extend([r'\begin{figure}[htbp]\centering', r'\includegraphics[width=\linewidth]{../figures/'+block['name']+'.pdf}',
                          r'\caption{'+tex_escape(block['caption'])+'}', r'\label{fig:'+block['name']+'}', r'\end{figure}'])
        elif kind == 'table':
            cols = ''.join(f'p{{{.89*w:.3f}\\linewidth}}' for w in block['widths'])
            lines.extend([r'\begin{table}[htbp]\centering\small', r'\setlength{\tabcolsep}{3pt}', r'\begin{tabular}{'+cols+r'}\toprule',
                          ' & '.join(tex_escape(v) for v in block['headers'])+r'\\\midrule'])
            lines.extend(' & '.join(tex_escape(str(v)) for v in row)+r'\\' for row in block['rows'])
            lines.extend([r'\bottomrule\end{tabular}', r'\caption{'+tex_escape(block['caption'])+'}', r'\end{table}'])
    lines.extend([r'\clearpage', r'\bibliographystyle{unsrt}', r'\bibliography{references}',
                  r'\section*{Report on the Use of AI}'])
    lines.extend(tex_escape(p)+'\n' for p in article['ai_report'])
    lines.append(r'\end{document}')
    (PAPER/'paper.tex').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def write_bibliography():
    (PAPER/'references.bib').write_text(r'''@misc{upc2026,
  author={{University Physics Competition}}, title={2026 Competition: Problem B --- Predicting FIFA Penalty Trajectories},
  year={2026}, howpublished={\url{https://university-physics-competition.com/2026-competition}}, note={Accessed 7 November 2026}}
@article{myers2013,
  author={Myers, T. G. and Mitchell, S. L.}, title={A mathematical analysis of the motion of an in-flight soccer ball},
  journal={Sports Engineering}, volume={16}, number={1}, pages={29--41}, year={2013}, doi={10.1007/s12283-012-0105-8}}
@misc{ifab,
  author={{The International Football Association Board}}, title={Laws of the Game: Law 2, The Ball},
  year={2026}, howpublished={\url{https://www.theifab.com/laws/latest/the-ball/}}, note={Accessed 7 November 2026}}
@article{asai2013,
  author={Asai, Takeshi and Seo, Kazuya}, title={Aerodynamic drag of modern soccer balls},
  journal={SpringerPlus}, volume={2}, pages={171}, year={2013}, doi={10.1186/2193-1801-2-171}}
@article{linthorne2011,
  author={Linthorne, Nicholas P. and Patel, Dipesh S.}, title={Optimum Projection Angle for Attaining Maximum Distance in a Soccer Punt Kick},
  journal={Journal of Sports Science and Medicine}, volume={10}, number={1}, pages={203--214}, year={2011},
  url={https://pmc.ncbi.nlm.nih.gov/articles/PMC3737918/}}
@misc{upcrules,
  author={{University Physics Competition}}, title={Contest Rules}, year={2026},
  howpublished={\url{https://uphysicsc.com/contestrules.html}}, note={Rules 5--6; accessed 7 November 2026}}
''', encoding='utf-8')


def build_pdf():
    log = []
    compiler = next((p for p in ['latexmk', 'pdflatex', 'xelatex'] if shutil.which(p)), None)
    compiled = False
    if compiler:
        command = [compiler, '-pdf', '-interaction=nonstopmode', '-halt-on-error', 'paper.tex'] if compiler == 'latexmk' else [compiler, '-interaction=nonstopmode', '-halt-on-error', 'paper.tex']
        try:
            proc = subprocess.run(command, cwd=PAPER, text=True, capture_output=True, timeout=120)
            log.append(proc.stdout+proc.stderr)
            compiled = proc.returncode == 0
            if compiled and compiler != 'latexmk':
                bib = subprocess.run(['bibtex', 'paper'], cwd=PAPER, text=True, capture_output=True, timeout=60)
                log.append(bib.stdout+bib.stderr)
                for _ in range(2):
                    proc = subprocess.run(command, cwd=PAPER, text=True, capture_output=True, timeout=120)
                    log.append(proc.stdout+proc.stderr)
                compiled = bib.returncode == 0 and proc.returncode == 0
        except (OSError, subprocess.TimeoutExpired) as exc:
            log.append(str(exc))
    else:
        # An actual invocation records the missing compiler, rather than implying success.
        try:
            subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'paper.tex'], cwd=PAPER, check=True, timeout=60)
        except (OSError, subprocess.SubprocessError) as exc:
            log.append('LaTeX compilation attempt unavailable: '+str(exc))
    if not compiled:
        try:
            import reportlab  # noqa: F401
            runtime = Path(sys.executable)
        except ImportError:
            runtime = Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
        if not runtime.exists():
            raise RuntimeError('No LaTeX compiler or ReportLab Python runtime available')
        proc = subprocess.run([str(runtime), '-m', 'src.render_pdf'], cwd=ROOT, text=True, capture_output=True, timeout=120)
        log.append(proc.stdout+proc.stderr)
        proc.check_returncode()
    (PAPER/'build.log').write_text('\n'.join(log), encoding='utf-8')
    status = dict(latex_compiled=compiled, pdf_exists=(PAPER/'paper.pdf').exists(),
                  renderer=compiler if compiled else 'ReportLab fallback',
                  submission_ready=False, blockers=['TEAM_NUMBER placeholder', 'Complete exact AI input/output appendix must be appended and reviewed'])
    (PAPER/'build_status.json').write_text(json.dumps(status, indent=2), encoding='utf-8')
    print(json.dumps(status), flush=True)


if __name__ == '__main__':
    write_paper()
    build_pdf()
