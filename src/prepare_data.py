"""
prepare_data.py - shared cleaning & encoding for the whole team.

Run from the project root:
    python src/prepare_data.py

Reads : data/student_lifestyle_raw.csv
Writes: data/student_lifestyle_clean.csv
        outputs/results/data_quality_report.txt
        outputs/results/group_cutoffs.json   (tertile cut-offs, for the slides)

Every teammate must use the grouping columns created here so that
"high vs low social activity" means exactly the same thing everywhere.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ----------------------------------------------------------------- paths ---
ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "student_lifestyle_raw.csv"
CLEAN_PATH = ROOT / "data" / "student_lifestyle_clean.csv"
REPORT_PATH = ROOT / "outputs" / "results" / "data_quality_report.txt"
CUTOFFS_PATH = ROOT / "outputs" / "results" / "group_cutoffs.json"

# --------------------------------------------------------------- settings ---
HOUR_COLS = [
    "Study_Hours_Per_Day",
    "Extracurricular_Hours_Per_Day",
    "Sleep_Hours_Per_Day",
    "Social_Hours_Per_Day",
    "Physical_Activity_Hours_Per_Day",
]
GPA_COL = "GPA"
STRESS_COL = "Stress_Level"
REQUIRED = HOUR_COLS + [GPA_COL, STRESS_COL]

STRESS_MAP = {"low": 1, "moderate": 2, "medium": 2, "high": 3}
STRESS_LABELS = {1: "Low", 2: "Moderate", 3: "High"}

GPA_MAX = 4.0              # change if your dataset uses another scale
HOURS_TOTAL = 24.0
HOURS_TOL = 0.05           # tolerance when testing "sums to 24"

SLEEP_SHORT_BELOW = 6.0    # < 6 h  -> Short
SLEEP_LONG_ABOVE = 8.0     # > 8 h  -> Long ; 6-8 h inclusive -> Normal
GPA_LOW_BELOW = 3.0        # < 3.0 -> "<3.0" ; 3.0-3.5 -> "3.0-3.5" ; > 3.5 -> ">3.5"
GPA_HIGH_ABOVE = 3.5

log_lines = []


def log(msg=""):
    print(msg)
    log_lines.append(msg)


# ---------------------------------------------------------------- helpers ---
def normalise_columns(df):
    """Match column names case/space-insensitively to the expected names."""
    wanted = {c.lower().replace(" ", "_"): c for c in REQUIRED + ["Student_ID"]}
    rename = {}
    for col in df.columns:
        key = col.strip().lower().replace(" ", "_")
        if key in wanted:
            rename[col] = wanted[key]
    return df.rename(columns=rename)


def tertile_group(series, name):
    """Low / Medium / High using the 1/3 and 2/3 quantiles.

    Values <= q33 -> Low, <= q67 -> Medium, otherwise High. Cut-off rules are
    deterministic even with many tied values (hours are often rounded).
    Returns (ordered categorical series, cutoffs dict).
    """
    q1, q2 = series.quantile([1 / 3, 2 / 3])
    grp = np.select([series <= q1, series <= q2], ["Low", "Medium"], default="High")
    cat = pd.Categorical(grp, categories=["Low", "Medium", "High"], ordered=True)
    return cat, {"variable": name, "q33": float(q1), "q67": float(q2)}


# Main cleaning pipeline, called from run_all.py (or directly from the command line).
def main():
    if not RAW_PATH.exists():
        sys.exit(f"Raw file not found: {RAW_PATH}\n"
                 "Download it from Kaggle and save it there (never edit it by hand).")

    df = normalise_columns(pd.read_csv(RAW_PATH))
    missing_cols = [c for c in REQUIRED if c not in df.columns]
    if missing_cols:
        sys.exit(f"Missing expected columns: {missing_cols}\nFound: {list(df.columns)}")

    log("=== DATA QUALITY REPORT ===")
    log(f"Raw shape: {df.shape[0]} rows x {df.shape[1]} columns")
    n_start = len(df)

    # ---- 1. missing values
    miss = df[REQUIRED].isna().sum()
    log("\n[1] Missing values per column:")
    log(miss.to_string())
    df = df.dropna(subset=REQUIRED)
    log(f"-> dropped {n_start - len(df)} rows with missing values")

    # ---- 2. duplicates (ignore Student_ID, which is unique by design)
    n_before = len(df)
    id_free = [c for c in df.columns if c != "Student_ID"]
    n_dup = int(df.duplicated(subset=id_free).sum())
    log(f"\n[2] Fully duplicated records (ignoring Student_ID): {n_dup}")
    if "Student_ID" in df.columns:
        log(f"    Duplicated Student_IDs: {int(df['Student_ID'].duplicated().sum())}")
    df = df.drop_duplicates(subset=id_free)
    log(f"-> dropped {n_before - len(df)} duplicate rows")

    # ---- 3. numeric types + impossible values
    for c in HOUR_COLS + [GPA_COL]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    bad_hours = (df[HOUR_COLS] < 0).any(axis=1) | (df[HOUR_COLS] > HOURS_TOTAL).any(axis=1)
    bad_gpa = (df[GPA_COL] < 0) | (df[GPA_COL] > GPA_MAX)
    bad = bad_hours | bad_gpa | df[HOUR_COLS + [GPA_COL]].isna().any(axis=1)
    log(f"\n[3] Impossible values: hours <0 or >24: {int(bad_hours.sum())}, "
        f"GPA outside 0-{GPA_MAX}: {int(bad_gpa.sum())}")
    df = df[~bad].copy()
    log(f"-> dropped {int(bad.sum())} rows; {len(df)} remain")

    # ---- 4. do the daily hours sum to 24 ?
    total = df[HOUR_COLS].sum(axis=1)
    sums_to_24 = (total - HOURS_TOTAL).abs() <= HOURS_TOL
    log(f"\n[4] Sum of the 5 hour columns: min={total.min():.2f}, "
        f"mean={total.mean():.2f}, max={total.max():.2f}")
    log(f"    Rows summing to 24 h (+/-{HOURS_TOL}): {int(sums_to_24.sum())} "
        f"({100 * sums_to_24.mean():.1f}%)")
    if sums_to_24.mean() > 0.95:
        log("    NOTE: hours form a ~24 h budget -> more of one habit means less of another "
            "(compositional constraint; mention in limitations / SWOT).")
    df["hours_total"] = total.round(2)

    # ---- 5. encode stress (ordinal) and keep the label
    raw_stress = df[STRESS_COL]
    if pd.api.types.is_numeric_dtype(raw_stress):
        df["Stress_Level_Num"] = raw_stress.astype(int)
    else:
        df["Stress_Level_Num"] = raw_stress.astype(str).str.strip().str.lower().map(STRESS_MAP)
    unknown = df["Stress_Level_Num"].isna()
    if unknown.any():
        log(f"\n[5] WARNING: {int(unknown.sum())} rows with unrecognised stress label "
            f"{sorted(raw_stress[unknown].astype(str).unique())} -> dropped")
        df = df[~unknown].copy()
    df["Stress_Level_Num"] = df["Stress_Level_Num"].astype(int)
    df[STRESS_COL] = pd.Categorical(
        df["Stress_Level_Num"].map(STRESS_LABELS),
        categories=["Low", "Moderate", "High"], ordered=True)
    log("\n[5] Stress level counts:")
    log(df[STRESS_COL].value_counts().sort_index().to_string())

    # ---- 6. shared grouping columns
    cutoffs = {}
    df["social_group"], cutoffs["social"] = tertile_group(
        df["Social_Hours_Per_Day"], "Social_Hours_Per_Day")
    df["extracurricular_group"], cutoffs["extracurricular"] = tertile_group(
        df["Extracurricular_Hours_Per_Day"], "Extracurricular_Hours_Per_Day")
    df["activity_group"], cutoffs["activity"] = tertile_group(
        df["Physical_Activity_Hours_Per_Day"], "Physical_Activity_Hours_Per_Day")

    sleep = df["Sleep_Hours_Per_Day"]
    df["sleep_group"] = pd.Categorical(
        np.select([sleep < SLEEP_SHORT_BELOW, sleep > SLEEP_LONG_ABOVE],
                  ["Short", "Long"], default="Normal"),
        categories=["Short", "Normal", "Long"], ordered=True)

    gpa = df[GPA_COL]
    band_labels = [f"<{GPA_LOW_BELOW:g}", f"{GPA_LOW_BELOW:g}-{GPA_HIGH_ABOVE:g}",
                   f">{GPA_HIGH_ABOVE:g}"]
    df["gpa_band"] = pd.Categorical(
        np.select([gpa < GPA_LOW_BELOW, gpa > GPA_HIGH_ABOVE],
                  [band_labels[0], band_labels[2]], default=band_labels[1]),
        categories=band_labels, ordered=True)

    log("\n[6] Group sizes:")
    for col in ["social_group", "extracurricular_group", "activity_group",
                "sleep_group", "gpa_band"]:
        counts = df[col].value_counts().sort_index()
        log(f"  {col}: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    cutoffs["sleep"] = {"short_below": SLEEP_SHORT_BELOW, "long_above": SLEEP_LONG_ABOVE}
    cutoffs["gpa_band"] = {"low_below": GPA_LOW_BELOW, "high_above": GPA_HIGH_ABOVE}

    # ---- 7. save
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    CUTOFFS_PATH.write_text(json.dumps(cutoffs, indent=2))
    log(f"\nFinal shape: {df.shape[0]} rows x {df.shape[1]} columns "
        f"({n_start - len(df)} rows removed in total)")
    log(f"Saved: {CLEAN_PATH.relative_to(ROOT)}")
    REPORT_PATH.write_text("\n".join(log_lines) + "\n")


if __name__ == "__main__":
    main()