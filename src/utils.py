"""
utils.py - helpers shared by all teammates' notebooks.

In a notebook (notebooks live one folder below the project root):
    import sys; sys.path.append("../src")
    from utils import *
    df = load_clean()
    set_style()
    ...
    save_fig(fig, "t1_fig01_hist_study")      # -> outputs/figures/t1_fig01_hist_study.png
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLEAN_PATH = ROOT / "data" / "student_lifestyle_clean.csv"
FIG_DIR = ROOT / "outputs" / "figures"
TABLE_DIR = ROOT / "outputs" / "tables"

ORDERED = {
    "Stress_Level": ["Low", "Moderate", "High"],
    "social_group": ["Low", "Medium", "High"],
    "extracurricular_group": ["Low", "Medium", "High"],
    "activity_group": ["Low", "Medium", "High"],
    "sleep_group": ["Short", "Normal", "Long"],
}
# One colour per ordered level, reused everywhere (Low -> High)
PALETTE = {"Low": "#4C78A8", "Moderate": "#F58518", "Medium": "#F58518",
           "High": "#E45756", "Short": "#E45756", "Normal": "#4C78A8", "Long": "#F58518"}


def load_clean():
    """Load the cleaned CSV with ordered categorical columns restored."""
    if not CLEAN_PATH.exists():
        raise FileNotFoundError(f"{CLEAN_PATH} not found - run `python run_all.py` first.")
    df = pd.read_csv(CLEAN_PATH)
    for col, cats in ORDERED.items():
        if col in df.columns:
            df[col] = pd.Categorical(df[col], categories=cats, ordered=True)
    return df


def set_style():
    """Same plot style for every figure in the presentation."""
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.figsize": (7, 4.5), "figure.dpi": 100, "savefig.dpi": 200,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.25,
        "axes.titlesize": 14, "axes.labelsize": 12, "legend.frameon": False,
    })


def save_fig(fig, name):
    """Save a matplotlib figure as PNG into outputs/figures/ (used by the PPT)."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / f"{name}.png"
    fig.savefig(path, bbox_inches="tight")
    print(f"saved {path.relative_to(ROOT)}")
    return path


def save_table(table, name):
    """Save a DataFrame as CSV into outputs/tables/."""
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    path = TABLE_DIR / f"{name}.csv"
    table.to_csv(path)
    print(f"saved {path.relative_to(ROOT)}")
    return path


def summary_table(df, cols):
    """Descriptive statistics: location and variability, one row per variable."""
    rows = {}
    for c in cols:
        x = df[c].dropna()
        mode = x.mode()
        rows[c] = {
            "n": len(x), "mean": x.mean(), "median": x.median(),
            "mode": mode.iloc[0] if len(mode) else np.nan,
            "std": x.std(), "variance": x.var(),
            "min": x.min(), "Q1": x.quantile(.25), "Q3": x.quantile(.75), "max": x.max(),
            "IQR": x.quantile(.75) - x.quantile(.25), "range": x.max() - x.min(),
            "skewness": x.skew(), "kurtosis": x.kurt(),
        }
    return pd.DataFrame(rows).T.round(3)


def stem_and_leaf(values, leaf_digits=1, title=None):
    """Print a stem-and-leaf plot (Python has no built-in one).

    Values are scaled so the last kept digit is the leaf, e.g. GPA 3.47 with
    leaf_digits=1 -> stem 3.4 | leaf 7  (stems are in tenths, leaves in hundredths).
    Returns the text as well so it can be saved or pasted onto a slide.
    """
    x = np.sort(np.asarray(pd.Series(values).dropna(), dtype=float))
    scaled = np.round(x * 10 ** leaf_digits * 10).astype(int)   # keep 1 extra digit as leaf
    stems, leaves = scaled // 10, scaled % 10
    lines = [title] if title else []
    lines.append(f"n = {len(x)}   (stem | leaf, leaf unit = {10 ** -(leaf_digits + 1):g})")
    width = max(len(str(s / 10 ** leaf_digits if leaf_digits else s)) for s in stems)
    for s in range(stems.min(), stems.max() + 1):
        lf = "".join(str(v) for v in leaves[stems == s])
        label = f"{s / 10 ** leaf_digits:.{leaf_digits}f}"
        lines.append(f"{label:>{width + 1}} | {lf}")
    text = "\n".join(lines)
    print(text)
    return text


def frequency_table(series):
    """Counts, percentages and cumulative percentages for a categorical variable."""
    counts = series.value_counts().sort_index()
    out = pd.DataFrame({"count": counts, "percent": (100 * counts / counts.sum()).round(1)})
    out["cumulative_percent"] = out["percent"].cumsum().round(1)
    return out