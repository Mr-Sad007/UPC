import numpy as np


def test_posterior_and_statistics_contract():
    from src.inference import posterior, summarize, draw_prior
    from src.models import observe
    rng = np.random.default_rng(17)
    params = draw_prior(rng, 256)
    obs = observe([[30, 2, 6]], cd=.25)[0]
    ensemble = posterior(obs, .01, rng, params=params)
    np.testing.assert_allclose(np.sum(ensemble['weights']), 1)
    assert np.all(ensemble['weights'] >= 0)
    assert 1 <= ensemble['ess'] <= 256+1e-8
    summary = summarize(ensemble['prediction'], ensemble['weights'])
    assert summary['crossing_probability'] > .99
    assert 0 <= summary['goal_probability'] <= 1
    assert np.linalg.eigvalsh(summary['covariance_m2']).min() > 0
    assert len(summary['mean_yz_m']) == 2
    assert summary['region_q95'] > 0


def test_summary_keeps_failed_mass():
    from src.inference import summarize
    result = dict(point=np.array([[11, 0, 1], [3, 0, .11]]),
                  time=np.array([.4, .2]), status=np.array(['goal_plane', 'ground_before_goal']))
    summary = summarize(result, np.array([.6, .4]))
    assert summary['goal_probability'] == .6
    assert summary['ground_before_goal_probability'] == .4
    assert summary['crossing_probability'] == .6
