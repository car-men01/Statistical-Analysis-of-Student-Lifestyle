"""
run_all.py - master script for the whole pipeline.

Usage (from the project root):
    python run_all.py

RIGHT NOW only step 1 (prepare_data.py) is active.
When the teammates' notebooks / .m files exist, uncomment the matching lines
in main() at the bottom.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(cmd, label):
    """Run a command from the project root; stop the pipeline if it fails."""
    print(f"\n{'=' * 60}\n>> {label}\n{'=' * 60}")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        sys.exit(f"\nFAILED: {label} (exit code {result.returncode})")


def prepare_data():
    run([sys.executable, "src/prepare_data.py"], "Step 1: clean data and create shared groups")


def run_notebook(path):
    """Execute a Python notebook in place (needs: pip install jupyter nbconvert)."""
    run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute",
         "--inplace", str(path)], f"Notebook: {path}")


def run_matlab(script):
    """Run a .m file with MATLAB if installed, otherwise with Octave, otherwise skip."""
    folder, name = Path(script).parent, Path(script).stem
    if shutil.which("matlab"):
        run(["matlab", "-batch", f"cd('{folder}'); {name}"], f"MATLAB: {script}")
    elif shutil.which("octave"):
        run(["octave", "--no-gui", "--eval", f"cd('{folder}'); {name}"], f"Octave: {script}")
    else:
        print(f"\n[skipped] {script} - neither MATLAB nor Octave found on PATH")


def main():
    # Step 1 - prepare the data (cleaning, encoding, grouping)
    prepare_data()                                   

    # Step 2: Python descriptive statistics (uncomment when notebooks exist)
    # run_notebook("teammate1_study/study_descriptive.ipynb")
    # run_notebook("teammate2_health/health_descriptive.ipynb")
    # run_notebook("teammate3_social/social_descriptive.ipynb")

    # Step 3: MATLAB / Octave inference (uncomment when .m files exist)
    # run_matlab("teammate1_study/study_inference.m")
    # run_matlab("teammate2_health/health_inference.m")
    # run_matlab("teammate3_social/social_inference.m")

    print("\nPipeline finished.")


if __name__ == "__main__":
    main()