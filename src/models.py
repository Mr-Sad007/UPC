"""SI-unit flight models, conditional state fitting and first-event roots."""
import numpy as np

MASS = .43
RADIUS = .11
AREA = np.pi * RADIUS**2
GRAVITY = 9.81
R0 = np.array([0., 0., RADIUS])
TIMES = np.array([.05, .10])
SUPPLIED = np.array([[1.50, .45, .44], [2.96, .86, .74]])


def observations(obs, times=TIMES):
    obs = np.asarray(obs, dtype=float)
    if obs.ndim == 2:
        obs = obs[None]
    times = np.asarray(times, dtype=float)
    if (obs.ndim != 3 or obs.shape[1:] != (2, 3)
            or times.shape != (2,) or not np.all(np.isfinite(obs))
            or not np.all(np.isfinite(times)) or not 0 < times[0] < times[1]):
        raise ValueError('Need finite (N,2,3) positions and two increasing positive times')
    return obs, times


def baseline_fit(obs, times=TIMES):
    obs, times = observations(obs, times)
    design = np.column_stack([times, .5*times**2])
    va = np.einsum('ij,njk->nik', np.linalg.inv(design), obs-R0)
    return va[:, 0], va[:, 1]


def baseline_crossing(v, a, last_time=.1):
    v, a = np.atleast_2d(v).astype(float), np.atleast_2d(a).astype(float)
    disc = v[:, 0]**2 + 22*a[:, 0]
    denom = v[:, 0] + np.sqrt(np.maximum(0, disc))
    tgoal = np.full(len(v), np.inf)
    valid = (disc > 0) & (denom > 0)
    tgoal[valid] = 22/denom[valid]
    tgoal[tgoal <= last_time] = np.inf
    tground = np.full(len(v), np.inf)
    entering_ground = (v[:, 2] < 0) | ((v[:, 2] == 0) & (a[:, 2] < 0))
    tground[entering_ground] = 0
    falling = (a[:, 2] < 0) & (v[:, 2] > 0)
    tground[falling] = -2*v[falling, 2]/a[falling, 2]
    isgoal = np.isfinite(tgoal) & (tgoal < tground)
    isground = ~isgoal & np.isfinite(tground)
    status = np.full(len(v), 'no_forward_crossing', dtype='U24')
    status[isgoal] = 'goal_plane'
    status[isground] = 'ground_before_goal'
    time = np.where(isgoal, tgoal, np.where(isground, tground, np.nan))
    point = R0 + time[:, None]*v + .5*time[:, None]**2*a
    return dict(point=point, time=time, status=status)


def _parameters(n, cd=.25, omega=None, rho=1.225, alpha=1.):
    cd = np.broadcast_to(np.asarray(cd, dtype=float), (n,))
    rho = np.broadcast_to(np.asarray(rho, dtype=float), (n,))
    alpha = np.broadcast_to(np.asarray(alpha, dtype=float), (n,))
    omega = np.broadcast_to(np.zeros(3) if omega is None else np.asarray(omega, dtype=float), (n, 3))
    if (np.any(cd < 0) or np.any(rho <= 0) or np.any(alpha < 0)
            or not all(np.all(np.isfinite(p)) for p in (cd, rho, alpha, omega))):
        raise ValueError('Nonfinite or nonphysical aerodynamic inputs')
    return cd, omega, rho, alpha


def acceleration(v, cd=.25, omega=None, rho=1.225, alpha=1., gravity=GRAVITY, mismatch=False):
    v = np.atleast_2d(v).astype(float)
    cd, omega, rho, alpha = _parameters(len(v), cd, omega, rho, alpha)
    return _acceleration(v, cd, omega, rho, alpha, gravity, mismatch)


def _acceleration(v, cd, omega, rho, alpha, gravity, mismatch):
    speed = np.linalg.norm(v, axis=1)
    k = rho*AREA/(2*MASS)
    lift = alpha*RADIUS
    if mismatch:
        # Declared stress-test physics, not a literature-calibrated lift law.
        spinratio = lift*np.linalg.norm(omega, axis=1)/np.maximum(speed, 1e-12)
        lift = lift/np.sqrt(1+(spinratio/.25)**2)
        cd = cd*(1+.2*np.tanh((25-speed)/5))
    a = -((k*cd*speed)[:, None])*v + (k*lift)[:, None]*np.cross(omega, v)
    a[:, 2] -= gravity
    return a


def _rhs(state, params, gravity, mismatch):
    return np.concatenate([state[:, 3:], _acceleration(state[:, 3:], *params, gravity, mismatch)], axis=1)


def _step(state, dt, params, gravity, mismatch):
    k1 = _rhs(state, params, gravity, mismatch)
    k2 = _rhs(state+dt*k1/2, params, gravity, mismatch)
    k3 = _rhs(state+dt*k2/2, params, gravity, mismatch)
    k4 = _rhs(state+dt*k3, params, gravity, mismatch)
    return state + dt*(k1+2*k2+2*k3+k4)/6


def observe(v, cd=.25, omega=None, rho=1.225, alpha=1., times=TIMES,
            dt=.01, gravity=GRAVITY, mismatch=False):
    v = np.atleast_2d(v).astype(float)
    times = np.asarray(times, dtype=float)
    if (dt <= 0 or not np.all(np.isfinite(v)) or np.any(np.diff(times) <= 0)
            or len(times) == 0 or times[0] <= 0):
        raise ValueError('Invalid integration inputs')
    params = _parameters(len(v), cd, omega, rho, alpha)
    state = np.concatenate([np.broadcast_to(R0, v.shape).copy(), v], axis=1)
    output, t = [], 0.
    for target in times:
        steps = max(1, int(np.ceil((target-t)/dt-1e-10)))
        h = (target-t)/steps
        for _ in range(steps):
            state = _step(state, h, params, gravity, mismatch)
        output.append(state[:, :3].copy())
        t = target
    return np.stack(output, axis=1)


def _hermite(left, right, u, dt):
    u = u[:, None]
    return ((2*u**3-3*u**2+1)*left[:, :3]
            +(u**3-2*u**2+u)*dt*left[:, 3:]
            +(-2*u**3+3*u**2)*right[:, :3]
            +(u**3-u**2)*dt*right[:, 3:])


def _root(left, right, axis, level, dt, increasing):
    lo, hi = np.zeros(len(left)), np.ones(len(left))
    for _ in range(36):
        mid = (lo+hi)/2
        value = _hermite(left, right, mid, dt)[:, axis]
        below = value < level if increasing else value > level
        lo = np.where(below, mid, lo)
        hi = np.where(below, hi, mid)
    u = (lo+hi)/2
    return u, _hermite(left, right, u, dt)


def propagate(v, cd=.25, omega=None, rho=1.225, alpha=1., dt=.01,
              gravity=GRAVITY, mismatch=False, max_time=2.):
    """Stop at first forward goal plane or downward ground contact, with roots."""
    v = np.atleast_2d(v).astype(float)
    if not np.all(np.isfinite(v)) or dt <= 0 or max_time <= 0:
        raise ValueError('Invalid integration inputs')
    n = len(v)
    params = _parameters(n, cd, omega, rho, alpha)
    state = np.concatenate([np.broadcast_to(R0, v.shape).copy(), v], axis=1)
    point, time = np.full((n, 3), np.nan), np.full(n, np.nan)
    status = np.full(n, 'no_forward_crossing', dtype='U24')
    initial_az = _acceleration(v, *params, gravity, mismatch)[:, 2]
    active = (v[:, 2] > 0) | ((v[:, 2] == 0) & (initial_az >= 0))
    status[~active], point[~active], time[~active] = 'ground_before_goal', R0, 0.
    steps = int(np.ceil(max_time/dt))
    for step in range(steps):
        ids = np.flatnonzero(active)
        if not len(ids):
            break
        left = state[ids]
        right = _step(left, dt, tuple(p[ids] for p in params), gravity, mismatch)
        bad = ~np.all(np.isfinite(right), axis=1)
        if np.any(bad):
            status[ids[bad]] = 'numerical_failure'
            active[ids[bad]] = False
        goal = (left[:, 0] < 11) & (right[:, 0] >= 11) & ~bad
        ground = (right[:, 2] <= RADIUS) & (right[:, 5] < 0) & ~bad
        event = goal | ground
        if np.any(event):
            eids = np.flatnonzero(event)
            ug, ud = np.full(len(eids), np.inf), np.full(len(eids), np.inf)
            pg, pd = np.zeros((len(eids), 3)), np.zeros((len(eids), 3))
            mg, md = goal[eids], ground[eids]
            if np.any(mg):
                ug[mg], pg[mg] = _root(left[eids[mg]], right[eids[mg]], 0, 11, dt, True)
            if np.any(md):
                ud[md], pd[md] = _root(left[eids[md]], right[eids[md]], 2, RADIUS, dt, False)
            choose = ug < ud
            target = ids[eids]
            point[target] = np.where(choose[:, None], pg, pd)
            time[target] = (step+np.minimum(ug, ud))*dt
            status[target] = np.where(choose, 'goal_plane', 'ground_before_goal')
            active[target] = False
        state[ids] = right
    return dict(point=point, time=time, status=status)


def fit_velocity(obs, cd=.25, omega=None, rho=1.225, alpha=1., times=TIMES):
    """Three-parameter Gauss-Newton fit; nuisance parameters stay fixed."""
    obs, times = observations(obs, times)
    n = len(obs)
    params = _parameters(n, cd, omega, rho, alpha)
    ballistic = obs-R0
    ballistic[:, :, 2] += .5*GRAVITY*times**2
    velocity = np.sum(times[None, :, None]*ballistic, axis=1)/np.sum(times**2)
    eps, converged = 1e-3, np.zeros(n, dtype=bool)
    for _ in range(4):
        trial = np.repeat(velocity[:, None, :], 4, axis=1)
        trial[:, 1:, :] += eps*np.eye(3)[None]
        expanded = tuple(np.repeat(p, 4, axis=0) for p in params)
        pred = observe(trial.reshape(-1, 3), *expanded[:3], alpha=expanded[3], times=times).reshape(n, 4, 2, 3)
        residual = (obs-pred[:, 0]).reshape(n, 6)
        jac = ((pred[:, 1:]-pred[:, :1])/eps).reshape(n, 3, 6).transpose(0, 2, 1)
        info = np.einsum('nki,nkj->nij', jac, jac)
        score = np.einsum('nki,nk->ni', jac, residual)
        delta = np.linalg.solve(info, score[..., None])[..., 0]
        velocity += delta
        converged = np.linalg.norm(delta, axis=1) < 1e-6
        if np.all(converged):
            break
    pred = observe(velocity, *params[:3], alpha=params[3], times=times)
    residual = (obs-pred).reshape(n, 6)
    return dict(velocity=velocity, residual=residual, sse=np.sum(residual**2, axis=1),
                covariance_unit=np.linalg.inv(info), information=info, converged=converged)


def in_goal(result, clearance=False):
    p = result['point']
    dy, low, high = (3.66-RADIUS, RADIUS, 2.44-RADIUS) if clearance else (3.66, 0, 2.44)
    return ((result['status'] == 'goal_plane') & (np.abs(p[:, 1]) < dy)
            & (p[:, 2] > low) & (p[:, 2] < high))
