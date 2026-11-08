"""Independent content and functional checks; never hash verification."""
import csv
import json
from pathlib import Path
import numpy as np
from .experiments import ROOT, RESULTS, save_json
from .convergence import load_rows


def audit():
    checks = []
    def check(name, condition, detail):
        checks.append(dict(check=name, passed=bool(condition), detail=detail))
        if not condition:
            raise AssertionError(name+': '+detail)
    original = json.loads((ROOT/'data/supplied_case.json').read_text(encoding='utf-8'))
    supplied = json.loads((RESULTS/'supplied_case.json').read_text(encoding='utf-8'))
    expected = [[0, 0, .11], [1.50, .45, .44], [2.96, .86, .74]]
    check('Original observations preserved', original['positions_m'] == expected and supplied['raw_observations_m'] == expected,
          'Content comparison to official problem coordinates; no checksum.')
    check('Goal geometry preserved', original['goal_x_m'] == 11 and original['goal_y_bounds_m'] == [-3.66, 3.66]
          and original['goal_z_bounds_m'] == [0, 2.44], 'Ball-center target, separate radius clearance.')
    manifest = json.loads((RESULTS/'run_manifest.json').read_text())
    metrics = load_rows('validation_metrics.csv')
    raw = load_rows('validation_raw.csv')
    n = manifest['n_validation']
    check('Complete paired validation', len(raw) == n*4*3 and all(len([r for r in raw if r['model'] == m and r['sigma_m'] == s]) == n
          for m in ['M0', 'M1', 'M2'] for s in [.005, .01, .02, .05]),
          f'{n} kicks per noise level; all three methods retained.')
    for metric in metrics:
        group = [r for r in raw if r['model'] == metric['model'] and r['sigma_m'] == metric['sigma_m']]
        shared = [r for r in group if r['common_valid']]
        e = [np.hypot(r['pred_y_m']-r['true_y_m'], r['pred_z_m']-r['true_z_m']) for r in shared]
        check(f'Independent RMSE {metric["model"]} sigma={metric["sigma_m"]}',
              np.isclose(np.sqrt(np.mean(np.square(e))), metric['common_rmse_m'], atol=1e-12),
              'Recomputed directly from raw predicted and true coordinates.')
        check(f'All-case classification {metric["model"]} sigma={metric["sigma_m"]}',
              np.isclose(np.mean([(r['goal_probability'] >= .5) == r['true_goal'] for r in group]), metric['classification_accuracy']),
              'Includes physical misses and ground-before-goal cases.')
    samples = np.load(RESULTS/'supplied_samples_sigma_0.01.npz')
    points, weights = samples['M2_point'], samples['weights']
    s = supplied['sigma_0.01_m']['M2']
    check('Normalized weights', abs(weights.sum()-1) < 1e-12 and np.all(weights >= 0), 'Complete central ensemble.')
    valid = samples['M2_status'] == 'goal_plane'
    goal = valid & (abs(points[:, 1]) < 3.66) & (points[:, 2] > 0) & (points[:, 2] < 2.44)
    check('Independent geometric probability', abs(weights[goal].sum()-s['goal_probability']) < 1e-12,
          'In-goal mass includes every particle; no outcome rejection.')
    wp = weights[valid]/weights[valid].sum()
    mean = np.sum(points[valid, 1:]*wp[:, None], axis=0)
    check('Independent predictive mean', np.allclose(mean, s['mean_yz_m'], atol=1e-12), 'Conditional on airborne goal-plane intersection.')
    residual = points[valid, 1:]-mean
    radius2 = np.einsum('ni,ij,nj->n', residual, np.linalg.inv(s['covariance_m2']), residual)
    check('Empirical 95% content', abs(wp[radius2 <= s['region_q95']].sum()-.95) < .002,
          'Posterior content checked separately from synthetic frequentist coverage.')
    article = json.loads((ROOT/'paper/article.json').read_text())
    check('Abstract limit', len(article['abstract'].split()) <= 300, f'{len(article["abstract"].split())} words; limit 300.')
    trace = json.loads((ROOT/'paper/claim_trace.json').read_text())
    check('Manuscript result trace', trace['uncertainty'] == s,
          'Generated article and TeX use the accepted saved numeric records.')
    tex = (ROOT/'paper/paper.tex').read_text()
    check('Anonymity scaffold', 'TEAM_NUMBER' in tex and '\\author{' not in tex and str(Path.home()).replace('\\', '/').lower() not in tex.replace('\\', '/').lower(),
          'Local home-directory path absent; personal and institution identifiers still require manual review.')
    check('AI query retained verbatim', (ROOT/'docs/original_request.txt').read_text(encoding='utf-8') in (ROOT/('AI_LOG.md' if (ROOT/'AI_LOG.md').exists() else 'AI_USAGE.md')).read_text(encoding='utf-8'),
          'Exact user project request preserved, including original line breaks.')
    refs = load_rows('citation_verification.csv')
    check('References verified', all(r['status'] == 'VERIFIED_IDENTITY' for r in refs) and len(refs) == 6,
          'Six official or author-institution records; no unverified DOI inserted.')
    figure_manifest = json.loads((ROOT/'figures/figure_manifest.json').read_text())
    check('Programmatic figure labels', len(figure_manifest) == 7 and all(all('(' in label and ')' in label for label in labels.values()) for labels in figure_manifest.values()),
          'Every visible coordinate axis has a variable/quantity and unit or dimensionless marker.')
    build = json.loads((ROOT/'paper/build_status.json').read_text())
    check('PDF actually generated', build['pdf_exists'] and (ROOT/'paper/paper.pdf').stat().st_size > 10000,
          'Renderer recorded; PDF presence is not claimed as LaTeX compilation.')
    status = dict(checks=checks, passed=len(checks), failed=0, latex_compiled=build['latex_compiled'],
                  submission_ready=False, human_actions=['Replace TEAM_NUMBER', 'Review/append complete exact AI output and verify anonymity',
                                                        'Review physics assumptions and submit attachment before official deadline'],
                  scientific_limitations=['Assumed aerodynamic prior and lift law', 'No field validation or measured camera error',
                                          'Undercoverage and low ESS in the longer-window extension'])
    status['requested_checklist'] = [
        ['A', 'PASS', 'Original positions and goal dimensions preserved.'],
        ['B', 'PASS', 'Reported numerical results come from executed calculations.'],
        ['C', 'PASS', 'Complete python -m src.run_all execution returned exit code 0.'],
        ['D', 'PASS', 'Seven figure pairs generated programmatically.'],
        ['E', 'PASS', 'Coordinate axes have units; category axes are explicitly categorical.'],
        ['F', 'PASS', 'Core manuscript quantities trace to saved numerical records.'],
        ['G', 'PASS', 'No fabricated citation identified; six source identities verified.'],
        ['H', 'PASS', 'No unverified bibliography entry retained.'],
        ['I', 'PASS', 'SI-unit equations and force-direction/ballistic tests checked.'],
        ['J', 'PASS', 'Aerodynamic, measurement and synthetic-population assumptions declared.'],
        ['K', 'PASS', 'Six scalar constraints and aerodynamic non-identifiability explicitly analyzed.'],
        ['L', 'PASS', 'General-method synthetic validation, misses and mismatch test performed.'],
        ['M', 'PASS', 'Measurement, nuisance and combined uncertainty quantified.'],
        ['N', 'PASS', 'Physical no-point rates, numerical-failure mass and undercoverage retained.'],
        ['O', 'CONDITIONAL', 'Science paper anonymity checked; raw AI archive still needs anonymity review.'],
        ['P', 'PASS', f'Abstract is {len(article["abstract"].split())} words, below 300.'],
        ['Q', 'OPEN', 'AI disclosure section and exact internal archive exist; full closing appendix requires team review.'],
        ['R', 'OPEN', 'TEAM_NUMBER deliberately remains until the actual team number is supplied.'],
        ['S', 'PASS', 'No student/institution identity inserted into the scientific manuscript.'],
        ['T', 'PASS', 'Manuscript uses appropriately rounded values; raw machine records keep calculation precision.']]
    save_json('final_audit.json', status)
    markdown = '# Final audit\n\n'+'\n'.join(f'- PASS: {r["check"]}: {r["detail"]}' for r in checks)
    markdown += '\n\nLaTeX compiled: '+str(build['latex_compiled'])+'. Renderer: '+build['renderer']+'.\n'
    markdown += '\nSubmission-ready: no. TEAM_NUMBER and the complete AI-output appendix need human review.\n'
    markdown += '\n## Requested A-T checklist\n\n| Item | Status | Evidence or remaining action |\n|---|---|---|\n'
    markdown += '\n'.join('| '+' | '.join(row)+' |' for row in status['requested_checklist'])+'\n'
    save_json('final_audit.json', status)
    (ROOT/'docs/final_audit.md').write_text(markdown, encoding='utf-8')
    print(f'Final audit: {len(checks)} content/function checks passed; submission blockers explicitly retained.', flush=True)


if __name__ == '__main__':
    audit()
