"""Numerical convergence diagnostics; never selects cases by prediction error."""
import csv
import numpy as np
from .experiments import (RESULTS, SEED, SIGMAS, synthetic_population, save_csv,
                          metric_table, draw_prior, posterior, summarize)


def load_rows(name):
    with (RESULTS/name).open(encoding='utf-8') as f:
        raw = list(csv.DictReader(f))
    for row in raw:
        for key, value in row.items():
            if value == '': row[key] = None
            elif value in ['True', 'False']: row[key] = value == 'True'
            else:
                try: row[key] = float(value)
                except ValueError: pass
    return raw


def convergence_checks():
    rows = load_rows('validation_raw.csv')
    manifest_n = len([r for r in rows if r['model'] == 'M2' and r['sigma_m'] == .005])
    mc = len(np.load(RESULTS/'supplied_samples_sigma_0.01.npz')['weights'])
    # Reconstruct the original random stream without repeating its integrations.
    rng = np.random.default_rng(SEED)
    for sigma in SIGMAS:
        rng.normal(0, sigma, (mc, 2, 3))
        draw_prior(rng, mc)
        rng.normal(0, sigma, (mc, 2, 3))
    pop = synthetic_population(rng, manifest_n)
    original = np.load(RESULTS/'synthetic_truth.npz')
    assert np.array_equal(pop['velocity'], original['velocity'])
    assert np.array_equal(pop['observations'], original['observations'])
    noise = rng.normal(size=pop['observations'].shape)
    np.savez_compressed(RESULTS/'validation_observations.npz',
                        true_early_positions=pop['observations'], standard_normal_noise=noise,
                        sigma_m=np.array(SIGMAS))
    refinement = []
    for row in rows:
        if row['model'] != 'M2' or row['ess'] >= 30:
            continue
        i, sigma = int(row['case_id']), row['sigma_m']
        # Fixed diagnostic substream, independent of performance and main experiment RNG.
        rrng = np.random.default_rng(SEED+700000+i)
        post = posterior(pop['observations'][i]+sigma*noise[i], sigma, rrng, n=10000)
        s = summarize(post['prediction'], post['weights'])
        before = np.array([row['pred_y_m'], row['pred_z_m']])
        after = np.array(s['mean_yz_m'])
        is_crossing = pop['truth']['status'][i] == 'goal_plane'
        error = after-pop['truth']['point'][i, 1:] if is_crossing else None
        covered = bool(error@np.linalg.solve(np.array(s['covariance_m2']), error) <= s['region_q95']) if is_crossing else None
        refinement.append(dict(case_id=i, sigma_m=sigma, original_particles=512,
                               original_ess=row['ess'], refined_particles=10000, refined_ess=post['ess'],
                               original_y_m=before[0], original_z_m=before[1],
                               refined_y_m=after[0], refined_z_m=after[1],
                               point_change_m=float(np.linalg.norm(after-before)),
                               original_error_m=row['error_m'], refined_error_m=float(np.linalg.norm(error)) if is_crossing else None,
                               original_covered=row['covered'], refined_covered=covered,
                               original_goal_probability=row['goal_probability'], refined_goal_probability=s['goal_probability']))
    if refinement:
        save_csv('particle_convergence.csv', refinement)
    # Correct failure/coverage aggregation after review, retaining all raw observations.
    # Current runs have no missing regions or numerical particle failures, so existing metrics agree.
    refresh_metrics()
    print(f'Convergence: refined all {len(refinement)} ESS<30 cases; original frozen main table retained.', flush=True)


def refresh_metrics():
    table = metric_table(load_rows('validation_raw.csv'))
    save_csv('validation_metrics.csv', table)
    save_csv('model_comparison.csv', table)
    for raw_name, summary_name in [('mismatch_raw.csv', 'mismatch_metrics.csv'), ('duration_raw.csv', 'duration_metrics.csv')]:
        save_csv(summary_name, metric_table(load_rows(raw_name)))


if __name__ == '__main__':
    convergence_checks()
