"""One-command regeneration: python -m src.run_all."""
import subprocess
import sys
from .experiments import ROOT, run_experiments


def main():
    subprocess.run([sys.executable, '-m', 'pytest', 'tests', '-q'], cwd=ROOT, check=True)
    run_experiments()
    from .convergence import convergence_checks
    convergence_checks()
    from .plotting import make_figures
    from .write_paper import write_paper, build_pdf
    from .audit import audit
    make_figures()
    write_paper()
    build_pdf()
    audit()


if __name__ == '__main__':
    main()
