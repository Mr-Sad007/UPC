"""Saved, paired experiments. Synthetic truth never enters an estimator."""
import csv
import json
import platform
import sys
import time
from pathlib import Path
import numpy as np
from .models import (R0, RADIUS, TIMES, SUPPLIED, baseline_fit, baseline_crossing,
                     fit_velocity, propagate, observe, in_goal)
from .inference import draw_prior, posterior, summarize, kde_mode

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT/'results'
SEED = 20261107
SIGMAS = [.005, .01, .02, .05]


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, np.ndarray):
        return clean(value.tolist())
    if isinstance(value, (np.integer, np.bool_)):
        return value.item()
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    return value


def save_json(name, value):
    RESULTS.mkdir(exist_ok=True)
    (RESULTS/name).write_text(json.dumps(clean(value), indent=2, allow_nan=False), encoding='utf-8')


def save_csv(name, rows):
    RESULTS.mkdir(exist_ok=True)
    if not rows:
        raise ValueError(f'No rows for {name}')
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with (RESULTS/name).open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows([{k: clean(row.get(k)) for k in keys} for row in rows])


def subset_prediction(pred, ids):
    return {k: v[ids] for k, v in pred.items()}


def synthetic_population(rng, n, mismatch=False, times=TIMES):
    speed = rng.uniform(22, 35, n)
    azimuth, elevation = rng.uniform(-22, 22, n), rng.uniform(5, 18, n)
    az, el = np.deg2rad(azimuth), np.deg2rad(elevation)
    velocity = speed[:, None]*np.column_stack([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
    params = draw_prior(rng, n)
    observations = observe(velocity, **params, times=times, dt=.0025, mismatch=mismatch)
    truth = propagate(velocity, **params, dt=.0025, mismatch=mismatch)
    return dict(velocity=velocity, params=params, observations=observations, truth=truth,
                speed_m_s=speed, azimuth_deg=azimuth, elevation_deg=elevation,
                mismatch=mismatch)


def supplied_case(rng, n=10000):
    output, summary_rows, convergence_rows = {}, [], []
    v0, a0 = baseline_fit(SUPPLIED)
    base = baseline_crossing(v0, a0)
    fit1 = fit_velocity(SUPPLIED)
    drag = propagate(fit1['velocity'])
    output['raw_observations_m'] = np.vstack([R0, SUPPLIED])
    output['times_s'] = [0, .05, .10]
    output['M0'] = dict(velocity_m_s=v0[0], effective_acceleration_m_s2=a0[0],
                        time_s=base['time'][0], point_m=base['point'][0], status=base['status'][0])
    output['M1'] = dict(velocity_m_s=fit1['velocity'][0], Cd=.25,
                        time_s=drag['time'][0], point_m=drag['point'][0],
                        status=drag['status'][0], residuals_m=fit1['residual'][0], sse_m2=fit1['sse'][0])
    for sigma in SIGMAS:
        print(f'Supplied case: sigma={sigma} m, N={n}', flush=True)
        noisy = SUPPLIED+rng.normal(0, sigma, (n, 2, 3))
        vb, ab = baseline_fit(noisy)
        pred0 = baseline_crossing(vb, ab)
        f1 = fit_velocity(noisy)
        pred1 = propagate(f1['velocity'])
        ensemble = posterior(SUPPLIED, sigma, rng, n=n)
        pred2, weights = ensemble['prediction'], ensemble['weights']
        summaries = {'M0': summarize(pred0), 'M1': summarize(pred1), 'M2': summarize(pred2, weights)}
        summaries['M2'].update(ess=ensemble['ess'], invalid_nuisance_fits=ensemble['invalid_fit_count'])
        summaries['M2']['goal_probability_mc_se'] = float(np.sqrt(np.sum(weights**2*(in_goal(pred2)-summaries['M2']['goal_probability'])**2)))
        for model, summary in summaries.items():
            row = dict(model=model, component='measurement_only' if model != 'M2' else 'combined', sigma_m=sigma,
                       mean_y_m=summary.get('mean_yz_m', [None, None])[0],
                       mean_z_m=summary.get('mean_yz_m', [None, None])[1],
                       std_y_m=summary.get('std_yz_m', [None, None])[0],
                       std_z_m=summary.get('std_yz_m', [None, None])[1],
                       goal_probability=summary['goal_probability'], crossing_probability=summary['crossing_probability'],
                       ground_probability=summary['ground_before_goal_probability'],
                       numerical_failure_probability=summary['numerical_failure_probability'], ess=summary.get('ess', n))
            summary_rows.append(row)
        output[f'sigma_{sigma:g}_m'] = summaries
        np.savez_compressed(RESULTS/f'supplied_samples_sigma_{sigma:g}.npz',
                            M0_point=pred0['point'], M0_time=pred0['time'], M0_status=pred0['status'],
                            M1_point=pred1['point'], M1_time=pred1['time'], M1_status=pred1['status'],
                            M2_point=pred2['point'], M2_time=pred2['time'], M2_status=pred2['status'],
                            weights=weights, **ensemble['params'], fitted_velocity=ensemble['fit']['velocity'],
                            fit_sse=ensemble['fit']['sse'])
        if sigma == .01:
            for count in [1000, 5000, 10000]:
                if count <= n:
                    s = summarize(subset_prediction(pred2, slice(0, count)), weights[:count])
                    convergence_rows.append(dict(N=count, mean_y_m=s['mean_yz_m'][0], mean_z_m=s['mean_yz_m'][1],
                                                 std_y_m=s['std_yz_m'][0], std_z_m=s['std_yz_m'][1],
                                                 goal_probability=s['goal_probability'], region_q95=s['region_q95']))
            valid = pred2['status'] == 'goal_plane'
            output['M2_kde_mode'] = kde_mode(pred2['point'][valid, 1:], weights[valid])
            representative = {k: np.sum(weights[:, None]*p, axis=0) if p.ndim == 2 else float(weights@p)
                              for k, p in ensemble['params'].items()}
            output['representative_nuisance'] = representative
            # Same posterior nuisance draws, but fixed observed positions: no conditional state noise.
            aero = propagate(ensemble['fit']['velocity'], **ensemble['params'])
            fm = fit_velocity(noisy, **representative)
            meas = propagate(fm['velocity'], **representative)
            output['uncertainty_components'] = dict(
                aerodynamic_only=summarize(aero, weights), measurement_only=summarize(meas),
                combined=summaries['M2'],
                interpretation='Aerodynamic-only keeps observations fixed and retains sigma=.01 likelihood; components are not additive variances.')
            for name, pred, w in [('aerodynamic_only', aero, weights), ('measurement_only', meas, None)]:
                s = summarize(pred, w)
                summary_rows.append(dict(model='M2', component=name, sigma_m=.01,
                                         mean_y_m=s['mean_yz_m'][0], mean_z_m=s['mean_yz_m'][1],
                                         std_y_m=s['std_yz_m'][0], std_z_m=s['std_yz_m'][1],
                                         goal_probability=s['goal_probability'], crossing_probability=s['crossing_probability']))
            representative_fit = fit_velocity(SUPPLIED, **representative)
            output['representative_velocity_m_s'] = representative_fit['velocity'][0]
    save_json('supplied_case.json', output)
    save_csv('uncertainty_summary.csv', summary_rows)
    save_csv('monte_carlo_convergence.csv', convergence_rows)
    return clean(output)


def metric_table(rows):
    table = []
    keys = sorted({(r['population'], r['sigma_m'], r['model']) for r in rows})
    for pop, sigma, model in keys:
        group = [r for r in rows if (r['population'], r['sigma_m'], r['model']) == (pop, sigma, model)]
        valid = [r for r in group if r.get('error_m') is not None]
        common = [r for r in valid if r.get('common_valid', True)]
        errors = np.array([r['error_m'] for r in valid])
        ce = np.array([r['error_m'] for r in common])
        airborne = [r for r in group if r['true_status'] == 'goal_plane']
        coverage = [bool(r.get('covered')) for r in airborne] if model == 'M2' else [r['covered'] for r in group if r.get('covered') is not None]
        table.append(dict(population=pop, sigma_m=sigma, model=model, n_cases=len(group),
                          n_true_crossings=len(airborne), n_coordinate_errors=len(valid), n_common=len(common),
                          mean_error_m=float(np.mean(errors)) if len(errors) else None,
                          median_error_m=float(np.median(errors)) if len(errors) else None,
                          p95_error_m=float(np.quantile(errors, .95)) if len(errors) else None,
                          rmse_m=float(np.sqrt(np.mean(errors**2))) if len(errors) else None,
                          common_rmse_m=float(np.sqrt(np.mean(ce**2))) if len(ce) else None,
                          common_mean_error_m=float(np.mean(ce)) if len(ce) else None,
                          common_median_error_m=float(np.median(ce)) if len(ce) else None,
                          common_p95_error_m=float(np.quantile(ce, .95)) if len(ce) else None,
                          mae_y_m=float(np.mean([r['abs_y_error_m'] for r in valid])) if valid else None,
                          mae_z_m=float(np.mean([r['abs_z_error_m'] for r in valid])) if valid else None,
                          no_point_rate_on_true_crossings=float(np.mean([r['pred_status'] != 'goal_plane' for r in airborne])) if airborne else None,
                          classification_accuracy=float(np.mean([r['classification_correct'] for r in group])),
                          coverage_95=float(np.mean(coverage)) if coverage else None,
                          coverage_n=len(coverage),
                          elapsed_s_per_case=float(np.mean([r['elapsed_s'] for r in group])),
                          minimum_ess=min([r['ess'] for r in group if r.get('ess') is not None], default=None),
                          median_ess=float(np.median([r['ess'] for r in group if r.get('ess') is not None])) if model == 'M2' else None,
                          numerical_failure_rate=float(np.mean([r['pred_status'] == 'numerical_failure' for r in group])),
                          mean_particle_numerical_failure_probability=float(np.mean([r.get('particle_numerical_failure_probability') or 0. for r in group])),
                          low_ess_cases=sum(r.get('ess', 1e9) is not None and r.get('ess', 1e9) < 30 for r in group)))
    return table


def validation(rng, pop, sigmas=SIGMAS, particles=512, times=TIMES, population='matched', progress=True):
    n, rows = len(pop['velocity']), []
    if np.array_equal(times, TIMES):
        obs = pop['observations']
    else:
        obs = observe(pop['velocity'], **pop['params'], times=times, dt=.0025, mismatch=pop['mismatch'])
    standard_noise = rng.normal(size=obs.shape)
    truth, true_goal = pop['truth'], in_goal(pop['truth'])
    for sigma in sigmas:
        noisy = obs+sigma*standard_noise
        started = time.perf_counter()
        v0, a0 = baseline_fit(noisy, times)
        pred0 = baseline_crossing(v0, a0, last_time=times[-1])
        cost0 = (time.perf_counter()-started)/n
        started = time.perf_counter()
        fit1 = fit_velocity(noisy, times=times)
        pred1 = propagate(fit1['velocity'])
        cost1 = (time.perf_counter()-started)/n
        m2_summaries, cost2 = [], []
        for start in range(0, n, 32):
            end = min(start+32, n)
            batch = end-start
            t = time.perf_counter()
            post = posterior(np.repeat(noisy[start:end], particles, axis=0), sigma, rng,
                             params=draw_prior(rng, batch*particles), groups=batch, times=times)
            elapsed = (time.perf_counter()-t)/batch
            for j in range(batch):
                ids = slice(j*particles, (j+1)*particles)
                s = summarize(subset_prediction(post['prediction'], ids), post['weights'][ids])
                s['ess'] = float(post['ess'][j])
                m2_summaries.append(s)
                cost2.append(elapsed)
            if progress and (start == 0 or end == n or end % 256 == 0):
                print(f'Validation {population}: sigma={sigma} m, {end}/{n}, {particles} particles/case', flush=True)
        for i in range(n):
            s = m2_summaries[i]
            svalid = s['mean_yz_m'] is not None
            common = (truth['status'][i] == 'goal_plane' and pred0['status'][i] == 'goal_plane'
                      and pred1['status'][i] == 'goal_plane' and svalid)
            for model, pred, cost in [('M0', pred0, cost0), ('M1', pred1, cost1), ('M2', None, cost2[i])]:
                yz = np.asarray(s['mean_yz_m']) if model == 'M2' and svalid else (pred['point'][i, 1:] if pred is not None else np.full(2, np.nan))
                status = ('goal_plane' if svalid else 'numerical_failure' if s['numerical_failure_probability'] > 0 else 'no_forward_crossing') if model == 'M2' else str(pred['status'][i])
                pg = s['goal_probability'] if model == 'M2' else float(in_goal(subset_prediction(pred, slice(i, i+1)))[0])
                valid = truth['status'][i] == 'goal_plane' and status == 'goal_plane'
                error = yz-truth['point'][i, 1:] if valid else np.full(2, np.nan)
                covered = False if model == 'M2' and truth['status'][i] == 'goal_plane' else None
                if valid and model == 'M2':
                    q = error@np.linalg.solve(np.array(s['covariance_m2']), error)
                    covered = bool(q <= s['region_q95'])
                row = dict(population=population, sigma_m=float(sigma), observation_duration_s=float(times[-1]),
                           case_id=i, model=model, true_status=str(truth['status'][i]), pred_status=status,
                           true_y_m=float(truth['point'][i, 1]) if truth['status'][i] == 'goal_plane' else None,
                           true_z_m=float(truth['point'][i, 2]) if truth['status'][i] == 'goal_plane' else None,
                           pred_y_m=float(yz[0]) if status == 'goal_plane' else None,
                           pred_z_m=float(yz[1]) if status == 'goal_plane' else None,
                           error_m=float(np.linalg.norm(error)) if valid else None,
                           abs_y_error_m=float(abs(error[0])) if valid else None,
                           abs_z_error_m=float(abs(error[1])) if valid else None,
                           common_valid=common, goal_probability=float(pg), true_goal=bool(true_goal[i]),
                           classification_correct=bool((pg >= .5) == true_goal[i]), covered=covered,
                           elapsed_s=float(cost), ess=s['ess'] if model == 'M2' else None,
                           speed_m_s=float(pop['speed_m_s'][i]), azimuth_deg=float(pop['azimuth_deg'][i]),
                           elevation_deg=float(pop['elevation_deg'][i]), Cd=float(pop['params']['cd'][i]),
                           spin_rad_s=float(np.linalg.norm(pop['params']['omega'][i])),
                           spin_axis_z=float(pop['params']['omega'][i, 2]/max(1e-12, np.linalg.norm(pop['params']['omega'][i]))))
                if model == 'M2':
                    row.update(crossing_probability=s['crossing_probability'],
                               ground_probability=s['ground_before_goal_probability'],
                               particle_numerical_failure_probability=s['numerical_failure_probability'])
                rows.append(row)
    return rows


def diagnostics(rng):
    rows = []
    # Structural rank uses dimensionless perturbations with stated physical scales.
    f = fit_velocity(SUPPLIED)
    theta = np.r_[f['velocity'][0], .25, [10., -15., 20.]]
    scales = np.array([30., 10., 10., .25, 40., 40., 40.])
    def forward(q):
        return observe(q[:3], cd=q[3], omega=q[4:])[0].ravel()
    jac = np.column_stack([(forward(theta+np.eye(7)[j]*scales[j]*1e-4)
                            -forward(theta-np.eye(7)[j]*scales[j]*1e-4))/(2e-4) for j in range(7)])
    u, singular, vh = np.linalg.svd(jac, full_matrices=True)
    save_json('identifiability.json', dict(observation_scalars=6, dynamic_parameters=7,
              dimensionless_parameter_scales=scales, singular_values_m=singular,
              rank=int(np.linalg.matrix_rank(jac)), null_direction_dimensionless=vh[-1],
              null_residual_norm_m=float(np.linalg.norm(jac@vh[-1])),
              note='Rank does not demonstrate practical precision; independent lift scale would add an exact spin-scale degeneracy.'))
    cd_grid = np.linspace(.12, .40, 41)
    fitted = fit_velocity(np.repeat(SUPPLIED[None], len(cd_grid), axis=0), cd=cd_grid)
    p = propagate(fitted['velocity'], cd=cd_grid)
    for i, cd in enumerate(cd_grid):
        rows.append(dict(Cd=float(cd), sse_m2=float(fitted['sse'][i]), y_m=p['point'][i, 1],
                         z_m=p['point'][i, 2], time_s=p['time'][i]))
    save_csv('drag_profile.csv', rows)
    # Only an independent refinement of the already-frozen simulator accuracy check.
    v = np.array([[31, 8, 7], [24, -5, 4], [34, 0, 8]])
    omega = np.array([[20, -30, 40], [0, 40, -20], [40, 10, 0]])
    reference = propagate(v, cd=.3, omega=omega, dt=.00125)
    rows = []
    for dt in [.02, .01, .005, .0025]:
        pred = propagate(v, cd=.3, omega=omega, dt=dt)
        rows.append(dict(dt_s=dt, max_point_difference_m=float(np.max(np.linalg.norm(pred['point']-reference['point'], axis=1))),
                         max_time_difference_s=float(np.max(np.abs(pred['time']-reference['time'])))))
    save_csv('numerical_convergence.csv', rows)
    assert rows[1]['max_point_difference_m'] < 1e-5


def sensitivity(rng, supplied, main_rows, n_duration=400, particles=256):
    rows = []
    representative = supplied['representative_nuisance']
    defaults = dict(cd=representative['cd'], omega=np.array(representative['omega']), rho=representative['rho'])
    grids = dict(Cd=np.linspace(.12, .40, 9), density_kg_m3=np.linspace(1.15, 1.30, 7),
                 spin_rad_s=np.linspace(0, 80, 9), spin_axis_angle_deg=np.linspace(0, 360, 13),
                 lift_scale=np.linspace(.5, 1.5, 7))
    axis = defaults['omega']/max(np.linalg.norm(defaults['omega']), 1e-12)
    for factor, grid in grids.items():
        for value in grid:
            params = dict(defaults)
            if factor == 'Cd': params['cd'] = value
            elif factor == 'density_kg_m3': params['rho'] = value
            elif factor == 'spin_rad_s': params['omega'] = axis*value
            elif factor == 'lift_scale': params['alpha'] = value
            else:
                angle = np.deg2rad(value)
                params['omega'] = 50*np.array([0, np.cos(angle), np.sin(angle)])
            fit = fit_velocity(SUPPLIED, **params)
            pred = propagate(fit['velocity'], **params)
            rows.append(dict(factor=factor, value=float(value), y_m=pred['point'][0, 1],
                             z_m=pred['point'][0, 2], time_s=pred['time'][0],
                             status=pred['status'][0], sse_m2=float(fit['sse'][0])))
    v = np.asarray(supplied['representative_velocity_m_s'])
    for axis_id, axis_name in enumerate('xyz'):
        plus, minus = v.copy(), v.copy()
        plus[axis_id] += .1
        minus[axis_id] -= .1
        pplus, pminus = propagate(plus, **defaults), propagate(minus, **defaults)
        derivative = (pplus['point'][0, 1:]-pminus['point'][0, 1:])/.2
        rows.append(dict(factor=f'initial_velocity_{axis_name}', value=.1,
                         dy_dv_s=derivative[0], dz_dv_s=derivative[1]))
    save_csv('sensitivity.csv', rows)
    binned = []
    for factor in ['speed_m_s', 'azimuth_deg', 'elevation_deg', 'Cd', 'spin_rad_s', 'spin_axis_z']:
        for model in ['M0', 'M1', 'M2']:
            group = [r for r in main_rows if r['model'] == model and r['sigma_m'] == .01 and r['common_valid']]
            x = np.array([r[factor] for r in group])
            edges = np.linspace(x.min(), x.max(), 6)
            for j in range(5):
                selected = [r for r in group if edges[j] <= r[factor] <= edges[j+1] and (j == 4 or r[factor] < edges[j+1])]
                if selected:
                    error = np.array([r['error_m'] for r in selected])
                    binned.append(dict(factor=factor, model=model, lower=edges[j], upper=edges[j+1],
                                       n=len(selected), rmse_m=float(np.sqrt(np.mean(error**2)))))
    save_csv('population_sensitivity.csv', binned)
    pop = synthetic_population(rng, n_duration)
    duration_rows, exclusions = [], []
    for duration in [.05, .10, .15, .20]:
        eligible = (pop['truth']['time'] > duration) | (pop['truth']['status'] == 'goal_plane')
        # No observations after ground contact; excluded cases remain counted explicitly.
        ids = np.flatnonzero(eligible)
        sub = {k: ({pk: pv[ids] for pk, pv in val.items()} if isinstance(val, dict)
                   else val[ids] if isinstance(val, np.ndarray) else val) for k, val in pop.items()}
        ext = validation(rng, sub, sigmas=[.01], particles=particles,
                         times=np.array([duration/2, duration]), population=f'extended_T_{duration:g}')
        duration_rows.extend(ext)
        exclusions.append(dict(duration_s=duration, generated=n_duration, eligible=len(ids),
                               excluded_ground_before_last_observation=n_duration-len(ids)))
    save_csv('duration_raw.csv', duration_rows)
    save_csv('duration_metrics.csv', metric_table(duration_rows))
    save_csv('duration_exclusions.csv', exclusions)
    # Prior sensitivity is a diagnostic, not a post-hoc selected winner.
    prior_rows = []
    for spin_max, bounds in [(40, (.12, .40)), (80, (.12, .40)), (120, (.12, .40)), (80, (.10, .50))]:
        p = posterior(SUPPLIED, .01, rng, params=draw_prior(rng, 10000, spin_max=spin_max, cd_bounds=bounds))
        s = summarize(p['prediction'], p['weights'])
        prior_rows.append(dict(spin_max_rad_s=spin_max, Cd_low=bounds[0], Cd_high=bounds[1],
                               mean_y_m=s['mean_yz_m'][0], mean_z_m=s['mean_yz_m'][1],
                               std_y_m=s['std_yz_m'][0], std_z_m=s['std_yz_m'][1],
                               goal_probability=s['goal_probability'], ess=p['ess']))
    save_csv('prior_sensitivity.csv', prior_rows)


def run_experiments(n=1000, particles=512, mc=10000, duration_n=400):
    RESULTS.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)
    started = time.perf_counter()
    diagnostics(rng)
    supplied = supplied_case(rng, mc)
    pop = synthetic_population(rng, n)
    np.savez_compressed(RESULTS/'synthetic_truth.npz', velocity=pop['velocity'],
                        observations=pop['observations'], true_point=pop['truth']['point'],
                        true_time=pop['truth']['time'], true_status=pop['truth']['status'], **pop['params'])
    rows = validation(rng, pop, particles=particles)
    save_csv('validation_raw.csv', rows)
    table = metric_table(rows)
    save_csv('validation_metrics.csv', table)
    save_csv('model_comparison.csv', table)
    mismatch = synthetic_population(rng, n, mismatch=True)
    mismatch_rows = validation(rng, mismatch, sigmas=[.01], particles=particles, population='mismatch')
    save_csv('mismatch_raw.csv', mismatch_rows)
    save_csv('mismatch_metrics.csv', metric_table(mismatch_rows))
    sensitivity(rng, supplied, rows, n_duration=duration_n, particles=min(256, particles))
    save_json('run_manifest.json', dict(seed=SEED, python=sys.version, numpy=np.__version__,
              platform=platform.platform(), n_validation=n, posterior_particles_per_validation_case=particles,
              supplied_mc_samples=mc, duration_generated_cases=duration_n, sigma_scenarios_m=SIGMAS,
              integrator='vectorized RK4, dt=0.01 s; truth dt=0.0025 s; cubic Hermite event roots, 36 bisections',
              elapsed_experiment_seconds=time.perf_counter()-started,
              result_scope='Synthetic assumed population. No measured camera noise or FIFA tracking data.',
              hash_checks='Not performed, by explicit user instruction'))
    print(f'Experiments completed in {time.perf_counter()-started:.1f} s', flush=True)
