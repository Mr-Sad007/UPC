import numpy as np


def test_synthetic_observations_and_metrics():
    from src.experiments import synthetic_population, metric_table
    from src.models import observe
    pop = synthetic_population(np.random.default_rng(19), 20)
    assert pop['observations'].shape == (20, 2, 3)
    np.testing.assert_allclose(pop['observations'], observe(pop['velocity'], **pop['params'], dt=.0025))
    assert set(np.unique(pop['truth']['status'])) <= {'goal_plane', 'ground_before_goal'}
    rows = [dict(case_id=i, model='M0', sigma_m=.01, true_status='goal_plane',
                 pred_status='goal_plane', error_m=float(i), abs_y_error_m=float(i),
                 abs_z_error_m=0., classification_correct=True, covered=None,
                 elapsed_s=.001, population='matched') for i in range(3)]
    table = metric_table(rows)
    assert len(table) == 1
    np.testing.assert_allclose(table[0]['rmse_m'], np.sqrt(5/3))
    assert table[0]['median_error_m'] == 1
    assert table[0]['n_cases'] == 3


def test_grouped_posterior_normalizes_each_case():
    from src.inference import posterior, draw_prior
    from src.models import observe
    rng = np.random.default_rng(22)
    obs = observe([[30, 0, 5], [27, 2, 6]])
    p = posterior(np.repeat(obs, 64, axis=0), .01, rng,
                  params=draw_prior(rng, 128), groups=2)
    np.testing.assert_allclose(p['weights'].reshape(2, 64).sum(axis=1), 1)
    assert len(p['ess']) == 2


def test_failed_regions_count_as_uncovered_and_particle_failures_reported():
    from src.experiments import metric_table
    rows = [dict(case_id=i, model='M2', sigma_m=.01, true_status='goal_plane',
                 pred_status='goal_plane' if i == 0 else 'no_forward_crossing',
                 error_m=0. if i == 0 else None, abs_y_error_m=0., abs_z_error_m=0.,
                 classification_correct=True, covered=True if i == 0 else None,
                 particle_numerical_failure_probability=0. if i == 0 else .1,
                 ess=10., elapsed_s=.001, population='test') for i in range(2)]
    table = metric_table(rows)[0]
    assert table['coverage_95'] == .5
    assert table['coverage_n'] == 2
    assert table['mean_particle_numerical_failure_probability'] == .05
    rows[0]['particle_numerical_failure_probability'] = None
    assert metric_table(rows)[0]['mean_particle_numerical_failure_probability'] == .05
