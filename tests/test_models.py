import importlib.util
import numpy as np
import pytest


def test_model_module_exists():
    assert importlib.util.find_spec('src.models') is not None


def test_baseline_exact_recovery_and_roots():
    from src.models import baseline_fit, baseline_crossing
    obs = np.array([[1.5, .45, .44], [2.96, .86, .74]])
    v, a = baseline_fit(obs)
    np.testing.assert_allclose(v[0], [30.4, 9.4, 6.9])
    np.testing.assert_allclose(a[0], [-16, -16, -12], atol=1e-10)
    out = baseline_crossing(v, a)
    t = out['time'][0]
    assert .1 < t < 1
    assert v[0, 0] + a[0, 0]*t > 0
    np.testing.assert_allclose(v[0, 0]*t + .5*a[0, 0]*t*t, 11, atol=1e-10)
    missing = baseline_crossing([[1, 0, 2]], [[-10, 0, -9.81]])
    assert missing['status'][0] != 'goal_plane'


def test_force_units_directions_and_work():
    from src.models import acceleration, AREA, MASS
    assert .037 < AREA < .039 and MASS == .43
    v = np.array([[30., 0, 0]])
    ad = acceleration(v, cd=.25, gravity=0)
    assert np.sum(ad*v) < 0 and ad[0, 0] < 0
    am = acceleration(v, cd=0, omega=[[0, 0, 10]], gravity=0)
    assert am[0, 1] > 0
    np.testing.assert_allclose(np.sum(am*v), 0, atol=1e-12)


def test_analytic_limits_and_event_precision():
    from src.models import observe, propagate
    v = np.array([[30., 2., 6.]])
    times = np.array([.05, .1])
    ballistic = observe(v, cd=0, times=times)
    expected = np.array([0, 0, .11]) + times[:, None]*v[0]
    expected[:, 2] -= .5*9.81*times**2
    np.testing.assert_allclose(ballistic[0], expected, atol=1e-10)
    straight = observe(v, cd=0, gravity=0, times=times)
    np.testing.assert_allclose(straight[0], np.array([0, 0, .11])+times[:, None]*v[0], atol=1e-10)
    goal = propagate(v, cd=0)
    assert goal['status'][0] == 'goal_plane'
    np.testing.assert_allclose(goal['time'], 11/30, atol=1e-10)
    np.testing.assert_allclose(goal['point'][0], [11, 2*11/30, .11+6*11/30-.5*9.81*(11/30)**2], atol=1e-9)


def test_ground_event_and_step_convergence():
    from src.models import propagate
    ground = propagate([[22, 0, .5]], cd=.2)
    assert ground['status'][0] == 'ground_before_goal'
    np.testing.assert_allclose(ground['point'][0, 2], .11, atol=1e-9)
    args = dict(v=[[31, 8, 7]], cd=.3, omega=[[20, -30, 40]])
    coarse = propagate(**args, dt=.01)
    fine = propagate(**args, dt=.0025)
    np.testing.assert_allclose(coarse['point'], fine['point'], atol=1e-5)


def test_state_fit_recovers_known_velocity():
    from src.models import observe, fit_velocity
    v = np.array([[30., 4., 6.], [25., -3., 4.]])
    omega = np.array([[20., -15., 10.], [-20., 5., 30.]])
    obs = observe(v, cd=.24, omega=omega)
    fit = fit_velocity(obs, cd=.24, omega=omega)
    np.testing.assert_allclose(fit['velocity'], v, atol=1e-5)
    assert np.max(fit['sse']) < 1e-12
    assert np.all(fit['converged'])


def test_invalid_observations_rejected():
    from src.models import baseline_fit, fit_velocity
    with pytest.raises(ValueError):
        baseline_fit([[np.nan, 0, 0], [2, 0, 0]])
    with pytest.raises(ValueError):
        fit_velocity([[1, 0, .2], [2, 0, .3]], times=[.1, .05])


def test_tangent_launch_may_accelerate_upward():
    from src.models import propagate, baseline_crossing
    result = propagate([[30, 0, 0]], cd=0, omega=[[0, -80, 0]])
    assert result['status'][0] == 'goal_plane'
    assert result['point'][0, 2] > .11
    result0 = baseline_crossing([[30, 0, 0]], [[0, 0, 2]])
    assert result0['status'][0] == 'goal_plane'

