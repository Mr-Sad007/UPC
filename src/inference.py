"""Explicit nuisance priors and conditional-velocity likelihood integration."""
import numpy as np
from .models import TIMES, fit_velocity, propagate, in_goal


def draw_prior(rng, n, spin_max=80., cd_bounds=(.12, .40), rho_bounds=(1.15, 1.30)):
    axis = rng.normal(size=(n, 3))
    axis /= np.linalg.norm(axis, axis=1)[:, None]
    return dict(cd=rng.uniform(*cd_bounds, n),
                omega=axis*rng.uniform(0, spin_max, n)[:, None],
                rho=rng.uniform(*rho_bounds, n))


def weighted_quantile(values, weights, quantiles):
    order = np.argsort(values)
    values, weights = np.asarray(values)[order], np.asarray(weights)[order]
    cdf = np.cumsum(weights)-weights/2
    cdf /= weights.sum()
    return np.interp(quantiles, cdf, values)


def region(points, weights):
    weights = weights/weights.sum()
    mean = np.sum(weights[:, None]*points, axis=0)
    centered = points-mean
    covariance = (centered*weights[:, None]).T@centered
    covariance += 1e-12*np.eye(2)
    radius2 = np.einsum('ni,ij,nj->n', centered, np.linalg.inv(covariance), centered)
    q95 = float(weighted_quantile(radius2, weights, .95))
    return mean, covariance, q95


def summarize(prediction, weights=None):
    n = len(prediction['time'])
    weights = np.ones(n)/n if weights is None else np.asarray(weights, dtype=float)
    weights = weights/weights.sum()
    status = prediction['status']
    valid = (status == 'goal_plane') & np.all(np.isfinite(prediction['point']), axis=1)
    probability = float(weights[valid].sum())
    result = dict(n=int(n), crossing_probability=probability,
                  goal_probability=float(weights[in_goal(prediction)].sum()),
                  radius_clearance_probability=float(weights[in_goal(prediction, True)].sum()),
                  ground_before_goal_probability=float(weights[status == 'ground_before_goal'].sum()),
                  no_forward_crossing_probability=float(weights[status == 'no_forward_crossing'].sum()),
                  numerical_failure_probability=float(weights[status == 'numerical_failure'].sum()),
                  status_counts={str(s): int(np.sum(status == s)) for s in np.unique(status)},
                  conditioning='Location statistics conditional on airborne goal-plane crossing')
    if np.sum(valid) < 3 or probability < 1e-12:
        result.update(mean_yz_m=None, covariance_m2=None, region_q95=None)
        return result
    p, w = prediction['point'][valid, 1:], weights[valid]/probability
    mean, cov, q95 = region(p, w)
    eig, vec = np.linalg.eigh(cov)
    result.update(mean_yz_m=mean.tolist(), covariance_m2=cov.tolist(),
                  std_yz_m=np.sqrt(np.diag(cov)).tolist(),
                  median_yz_m=[float(weighted_quantile(p[:, j], w, .5)) for j in range(2)],
                  marginal_95_yz_m=[weighted_quantile(p[:, j], w, [.025, .975]).tolist() for j in range(2)],
                  mean_crossing_time_s=float(w@prediction['time'][valid]),
                  crossing_time_95_s=weighted_quantile(prediction['time'][valid], w, [.025, .975]).tolist(),
                  region_q95=q95, ellipse_semiaxes_m=np.sqrt(q95*eig).tolist(),
                  ellipse_eigenvectors=vec.tolist(),
                  region_definition='Empirical 95% Mahalanobis ellipse; posterior content, not guaranteed frequentist coverage')
    return result


def posterior(obs, sigma, rng, n=10000, params=None, times=TIMES, conditional_noise=True, groups=1):
    """Laplace-integrated velocity, prior importance draws of nuisance physics.

    A broad uniform prior on each velocity component [-60,60] m/s with vx>0
    is locally constant. Far from its boundary the marginal likelihood is
    exp(-SSE/(2 sigma^2))/sqrt(det(J.T J)). Perturb-and-refit draws approximate
    the conditional velocity posterior without fitting extra physical unknowns.
    """
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError('sigma must be positive')
    params = draw_prior(rng, n) if params is None else params
    n = len(params['cd'])
    obs = np.broadcast_to(np.asarray(obs, float), (n, 2, 3)).copy()
    fit = fit_velocity(obs, **params, times=times)
    sign, logdet = np.linalg.slogdet(fit['information'])
    logweight = -.5*fit['sse']/sigma**2-.5*logdet
    feasible = ((sign > 0) & fit['converged'] & (fit['velocity'][:, 0] > 0)
                & np.all(np.abs(fit['velocity']) < 60, axis=1))
    logweight[~feasible] = -np.inf
    if not np.any(feasible):
        raise RuntimeError('All nuisance fits failed or violated velocity prior')
    grouped_logweight = logweight.reshape(groups, -1)
    if np.any(~np.isfinite(np.max(grouped_logweight, axis=1))):
        raise RuntimeError('A case has no feasible posterior fits')
    weights = np.exp(grouped_logweight-np.max(grouped_logweight, axis=1, keepdims=True))
    weights /= weights.sum(axis=1, keepdims=True)
    ess = 1/np.sum(weights**2, axis=1)
    weights = weights.ravel()
    velocity = fit['velocity']
    noise_fit = None
    if conditional_noise:
        noisy = obs+rng.normal(0, sigma, obs.shape)
        noise_fit = fit_velocity(noisy, **params, times=times)
        velocity = noise_fit['velocity']
    prediction = propagate(velocity, **params)
    if noise_fit is not None:
        failed = ~noise_fit['converged'] | np.any(np.abs(velocity) >= 60, axis=1) | (velocity[:, 0] <= 0)
        prediction['status'][failed] = 'numerical_failure'
        prediction['point'][failed] = np.nan
        prediction['time'][failed] = np.nan
    return dict(params=params, fit=fit, weights=weights, prediction=prediction,
                ess=float(ess[0]) if groups == 1 else ess, invalid_fit_count=int(np.sum(~feasible)),
                sigma_m=float(sigma), conditional_noise=conditional_noise)


def kde_mode(points, weights, grid_size=65):
    """Grid mode of a Gaussian KDE; bandwidth and grid are explicit diagnostics."""
    mean, cov, _ = region(points, weights)
    effective_n = 1/np.sum((weights/weights.sum())**2)
    bandwidth_cov = cov*effective_n**(-1/3)
    inv = np.linalg.inv(bandwidth_cov)
    bounds = np.array([weighted_quantile(points[:, j], weights, [.005, .995]) for j in range(2)])
    yy, zz = np.meshgrid(*[np.linspace(*b, grid_size) for b in bounds])
    grid = np.column_stack([yy.ravel(), zz.ravel()])
    density = np.empty(len(grid))
    weights = weights/weights.sum()
    for start in range(0, len(grid), 128):
        delta = grid[start:start+128, None]-points[None]
        q = np.einsum('gni,ij,gnj->gn', delta, inv, delta)
        density[start:start+128] = np.exp(-q/2)@weights
    return dict(mode_yz_m=grid[np.argmax(density)].tolist(),
                grid_spacing_yz_m=((bounds[:, 1]-bounds[:, 0])/(grid_size-1)).tolist(),
                bandwidth_covariance_m2=bandwidth_cov.tolist(), grid_size=grid_size)
