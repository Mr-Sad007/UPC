"""Publication plots from saved numerical artifacts only."""
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle
from .models import SUPPLIED, R0, observe, propagate

ROOT = Path(__file__).resolve().parents[1]
COLORS = {'M0': '#b95630', 'M1': '#437595', 'M2': '#248074'}
LABELS = {'M0': 'Constant acceleration', 'M1': 'Fixed drag', 'M2': 'Aerodynamic ensemble'}
FIGURE_LABELS = {}


def read_csv(name):
    with (ROOT/'results'/name).open(encoding='utf-8') as f:
        return list(csv.DictReader(f))


def save(fig, name):
    (ROOT/'figures').mkdir(exist_ok=True)
    fig.savefig(ROOT/'figures'/f'{name}.pdf', bbox_inches='tight')
    fig.savefig(ROOT/'figures'/f'{name}.png', dpi=190, bbox_inches='tight')
    labels = {}
    for i, ax in enumerate(fig.axes):
        labels[f'axis_{i}_x'] = ax.get_xlabel()
        labels[f'axis_{i}_y'] = ax.get_ylabel()
        if hasattr(ax, 'get_zlabel'):
            labels[f'axis_{i}_z'] = ax.get_zlabel()
    assert all('(' in label and ')' in label for label in labels.values())
    FIGURE_LABELS[name] = labels
    (ROOT/'figures'/'figure_manifest.json').write_text(json.dumps(FIGURE_LABELS, indent=2), encoding='utf-8')
    plt.close(fig)


def ellipse(ax, summary, **kwargs):
    mean, cov = np.array(summary['mean_yz_m']), np.array(summary['covariance_m2'])
    eig, vectors = np.linalg.eigh(cov)
    major = vectors[:, 1]
    axes = np.sqrt(summary['region_q95']*eig)
    angle = np.degrees(np.arctan2(major[1], major[0]))
    ax.add_patch(Ellipse(mean, 2*axes[1], 2*axes[0], angle=angle, fill=False, **kwargs))


def make_figures():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.grid': True, 'grid.alpha': .17, 'axes.axisbelow': True,
                         'figure.dpi': 120, 'savefig.facecolor': 'white',
                         'pdf.fonttype': 42, 'ps.fonttype': 42})
    supplied = json.loads((ROOT/'results'/'supplied_case.json').read_text(encoding='utf-8'))
    summary = supplied['sigma_0.01_m']['M2']
    samples = np.load(ROOT/'results'/'supplied_samples_sigma_0.01.npz')
    rng = np.random.default_rng(20261108)
    fig = plt.figure(figsize=(7.3, 4.8))
    ax = fig.add_subplot(111, projection='3d')
    for model in ['M0', 'M1', 'M2']:
        if model == 'M0':
            t = np.linspace(0, supplied['M0']['time_s'], 100)
            p = R0+t[:, None]*np.array(supplied['M0']['velocity_m_s'])+.5*t[:, None]**2*np.array(supplied['M0']['effective_acceleration_m_s2'])
        elif model == 'M1':
            t = np.linspace(.001, supplied['M1']['time_s'], 100)
            p = np.vstack([R0, observe(supplied['M1']['velocity_m_s'], times=t)[0]])
        else:
            representative_end = propagate(supplied['representative_velocity_m_s'], **supplied['representative_nuisance'])['time'][0]
            t = np.linspace(.001, representative_end, 100)
            p = np.vstack([R0, observe(supplied['representative_velocity_m_s'], times=t,
                                      **supplied['representative_nuisance'])[0]])
        label = LABELS[model] if model != 'M2' else 'Representative ensemble physics'
        ax.plot(*p.T, color=COLORS[model], label=label, lw=1.7)
    observed = np.vstack([R0, SUPPLIED])
    ax.scatter(*observed.T, color='black', s=24, label='Supplied observations', depthshade=False)
    gy = np.array([-3.66, 3.66, 3.66, -3.66, -3.66])
    gz = np.array([0, 0, 2.44, 2.44, 0])
    ax.plot(np.full(5, 11), gy, gz, color='.35', lw=1.1)
    ax.set(xlabel='$x$ (m)', ylabel='$y$ (m)', zlabel='$z$ (m)', xlim=(0, 11.5), ylim=(-3.8, 3.8), zlim=(0, 2.7))
    ax.view_init(elev=18, azim=-61)
    ax.set_box_aspect((11, 7.5, 3.6))
    ax.legend(loc='upper left', fontsize=7, frameon=False)
    fig.subplots_adjust(left=0, right=.96, bottom=.06, top=1)
    save(fig, 'trajectory')

    fig, ax = plt.subplots(figsize=(7.1, 4.5), layout='constrained')
    ids = rng.choice(len(samples['weights']), 3500, p=samples['weights'])
    points = samples['M2_point'][ids]
    ax.scatter(points[:, 1], points[:, 2], s=3, alpha=.13, color=COLORS['M2'], rasterized=True)
    ax.add_patch(Rectangle((-3.66, 0), 7.32, 2.44, fill=False, lw=1.4, color='.3', label='Goal rectangle'))
    ellipse(ax, summary, color=COLORS['M2'], lw=1.7, label='Empirical 95% ellipse')
    for model, marker in [('M0', 's'), ('M1', '^')]:
        p = supplied[model]['point_m']
        ax.scatter(p[1], p[2], s=54, marker=marker, color=COLORS[model], label=LABELS[model], zorder=5)
    mode = supplied['M2_kde_mode']['mode_yz_m']
    ax.scatter(*summary['mean_yz_m'], s=65, color=COLORS['M2'], marker='x', lw=2, label='Posterior mean', zorder=6)
    ax.scatter(*mode, s=90, color='black', marker='*', label='KDE mode', zorder=6)
    ax.set(xlabel='$y$ (m)', ylabel='$z$ (m)', xlim=(-3.9, 4.1), ylim=(-.08, 3.05))
    ax.set_aspect('equal', adjustable='box')
    ax.legend(loc='upper left', frameon=False, fontsize=7.5, ncol=2)
    save(fig, 'goal_plane')

    raw = read_csv('validation_raw.csv')
    selected = [r for r in raw if float(r['sigma_m']) == .01 and r['common_valid'] == 'True']
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.15), layout='constrained')
    for model in ['M0', 'M1', 'M2']:
        e = np.sort([float(r['error_m']) for r in selected if r['model'] == model])
        axes[0].plot(e, np.arange(1, len(e)+1)/len(e), color=COLORS[model], label=LABELS[model])
    axes[0].set(xlabel='Goal-plane error (m)', ylabel='Cumulative probability (1)', ylim=(0, 1.02))
    axes[0].legend(frameon=False, fontsize=7)
    p2 = [r for r in selected if r['model'] == 'M2']
    for axis, marker, color in [('y', 'o', COLORS['M1']), ('z', '+', COLORS['M2'])]:
        axes[1].scatter([float(r[f'true_{axis}_m']) for r in p2], [float(r[f'pred_{axis}_m']) for r in p2],
                        s=7, marker=marker, alpha=.35, color=color, label=f'{axis} coordinate', rasterized=True)
    limits = axes[1].get_xlim()
    axes[1].plot(limits, limits, color='.3', lw=.8)
    axes[1].set(xlabel='True coordinate (m)', ylabel='Ensemble mean coordinate (m)')
    axes[1].legend(frameon=False, fontsize=7)
    save(fig, 'validation')

    metrics = read_csv('validation_metrics.csv')
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.05), layout='constrained')
    for model in ['M0', 'M1', 'M2']:
        group = sorted([r for r in metrics if r['model'] == model], key=lambda r: float(r['sigma_m']))
        x = [1000*float(r['sigma_m']) for r in group]
        axes[0].plot(x, [float(r['common_rmse_m']) for r in group], 'o-', color=COLORS[model], label=LABELS[model], ms=4)
        axes[1].plot(x, [100*float(r['no_point_rate_on_true_crossings']) for r in group], 'o-', color=COLORS[model], ms=4)
    axes[0].set(xlabel=r'Coordinate noise $\sigma$ (mm)', ylabel='Paired goal-plane RMSE (m)')
    axes[1].set(xlabel=r'Coordinate noise $\sigma$ (mm)', ylabel='No point for airborne truth (%)')
    axes[0].legend(frameon=False, fontsize=7)
    save(fig, 'measurement_noise')

    duration = read_csv('duration_metrics.csv')
    fig, ax = plt.subplots(figsize=(5.8, 3.2), layout='constrained')
    for model in ['M0', 'M1', 'M2']:
        group = sorted([r for r in duration if r['model'] == model], key=lambda r: float(r['population'].split('_')[-1]))
        ax.plot([1000*float(r['population'].split('_')[-1]) for r in group],
                [float(r['common_rmse_m']) for r in group], 'o-', color=COLORS[model], label=LABELS[model], ms=4)
    ax.set(xlabel='Last observation time $T$ (ms)', ylabel='Paired goal-plane RMSE (m)')
    ax.legend(frameon=False, fontsize=8)
    save(fig, 'observation_duration')

    sensitivity = read_csv('sensitivity.csv')
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.05), layout='constrained')
    for ax, factor, label in [(axes[0], 'Cd', 'Drag coefficient $C_D$ (1)'),
                              (axes[1], 'spin_axis_angle_deg', 'Spin-axis angle in $y$-$z$ plane (deg)')]:
        g = [r for r in sensitivity if r['factor'] == factor]
        for coord, color, style in [('y', COLORS['M1'], '-'), ('z', COLORS['M2'], '--')]:
            ax.plot([float(r['value']) for r in g], [float(r[f'{coord}_m']) for r in g],
                    style, color=color, label=f'{coord} at goal plane')
        ax.set(xlabel=label, ylabel='Predicted coordinate (m)')
        ax.legend(frameon=False, fontsize=7)
    save(fig, 'aerodynamic_sensitivity')

    components = supplied['uncertainty_components']
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), layout='constrained')
    x = np.arange(3)
    names = ['measurement_only', 'aerodynamic_only', 'combined']
    for j, color in enumerate([COLORS['M1'], COLORS['M2']]):
        axes[0].bar(x+(j-.5)*.30, [components[name]['std_yz_m'][j] for name in names],
                    width=.28, color=color, label=['$y$', '$z$'][j])
    axes[0].set(xticks=x, xticklabels=['Position\nnoise only', 'Nuisance\nspread only', 'Combined'],
                xlabel='Uncertainty scenario (categorical)', ylabel='Coordinate standard deviation (m)')
    axes[0].legend(frameon=False)
    priors = read_csv('prior_sensitivity.csv')
    for j, color in enumerate([COLORS['M1'], COLORS['M2']]):
        axes[1].errorbar(np.arange(len(priors))+(j-.5)*.12,
                         [float(r[['mean_y_m', 'mean_z_m'][j]]) for r in priors],
                         yerr=[float(r[['std_y_m', 'std_z_m'][j]]) for r in priors],
                         fmt='o', color=color, capsize=3, ms=4)
    axes[1].set(xticks=np.arange(len(priors)), xticklabels=['40', '80', '120', '80; wide drag'],
                xlabel='Prior spin ceiling (rad/s)', ylabel=r'Mean coordinate $\pm$ 1 s.d. (m)')
    save(fig, 'uncertainty_components')
    print('Saved seven figure pairs (PDF and PNG).', flush=True)
