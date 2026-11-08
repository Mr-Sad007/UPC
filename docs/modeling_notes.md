# Information available in three positions

The supplied initial position is fixed: r(0)=(0,0,0.11) m. The two later positions provide SIX independent scalar observations, not nine constraints on the dynamics. If r(0) were noisy and estimated, its three observations would accompany three additional unknown initial coordinates. Times are treated as exact.

## Identifiability before fitting

| Model | Free dynamic parameters | Consequence |
|---|---:|---|
| Constant acceleration | initial velocity (3), effective acceleration (3) | Six equations, six unknowns; exact interpolation and no residual degrees of freedom |
| Gravity, fixed quadratic drag | velocity (3) | Three residual degrees of freedom; physically constrained fit |
| Gravity, unknown constant drag | velocity (3), Cd (1) | Formally overdetermined; short-window practical identifiability can still be weak |
| Gravity, drag and spin | velocity (3), Cd (1), spin vector (3) | At least seven unknowns for six observations; underdetermined |
| Independent spin and lift scale | preceding seven plus lift scale (1) | Eight unknowns; spin-scale product degeneracy as well |

Unknown density, diameter, mass, camera biases, wind or initial position increase ambiguity. Even with a fixed lift law, the spin component parallel to the initial velocity produces no initial Magnus force. A six-by-seven local sensitivity matrix has rank at most six; finite-time curvature does not remove its null space. Numerical rank and singular values must be examined with stated parameter scaling. A solver returning a unique optimum would not prove uniqueness of the physical inverse problem.

## Analytical baseline and noise amplification

For h=0.05 s, let d1=r(h)-r0 and d2=r(2h)-r0. Then a=(d2-2d1)/h^2 and v0=(4d1-d2)/(2h). Units are m/s^2 and m/s. The three accelerations describe the observed window only; they are not constant physical aerodynamic forces.

For a general extrapolation time t, the coefficients of noisy r1 and r2 are c1=2t/h-(t/h)^2 and c2=((t/h)^2-t/h)/2. Independent coordinate noise of standard deviation sigma therefore gives sigma*sqrt(c1^2+c2^2) at fixed t. Goal time is itself uncertain and couples all three axes. Acceleration noise scales as sqrt(5)*sigma/h^2, while initial-velocity noise scales as sqrt(17)*sigma/(2h). Small early-coordinate errors can thus be magnified far beyond the observed window.

The equation x(t)=11 can have two positive roots or no real crossing. Select the first forward crossing after the observation window with vx>0. A later returning root is not the first goal crossing. A missing root is a reported failure, never silently deleted.

## Reduced physical inference

Use drag and a fixed, explicitly assumed lift law. Do not independently fit both spin rate and lift coefficient. The spin vector is a nuisance parameter with a declared prior. Fit three initial-velocity components conditional on each nuisance draw; use the six-position Gaussian likelihood to reweight draws. Integrate conditional velocity uncertainty rather than treating fitted velocity as exact. Report effective sample size, prior dependence, residuals, and coverage under synthetic experiments.

The likelihood cannot supply a camera error scale: the problem provides none. All sigma values (0.005, 0.01, 0.02, 0.05 m) are sensitivity scenarios. A central result is conditional on sigma=0.01 m and the chosen aerodynamic prior, not an unconditional measured confidence statement.

## Physical boundary

The requested target is the first intersection of the BALL CENTER with x=11. The rectangular point-in-goal probability is geometric, not a probability of beating a goalkeeper. Finite-radius clearance is reported separately. Contact at z=radius terminates free flight; ground-before-plane cases are retained with their failure classification. No ground-bounce or post collision model is assumed.
