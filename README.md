# Statistical-Analysis-of-Student-Lifestyle

## Project Idea
**Statistical analysis of the impact of daily habits (study, sleep, activity, socializing) on student academic performance and stress.**

> Central question: *Which daily habits are statistically associated with GPA and stress, and how strong are those associations?*

*(Title slide must also include: short history/background, other relevant info, and what is already known vs. what is not.)*

## Dataset (Kaggle)
https://www.kaggle.com/datasets/steve1215rogg/student-lifestyle-dataset/data

- ~2000 students, one row each (verify after download)
- Variables (verify names): `Student_ID`, `Study_Hours_Per_Day`, `Extracurricular_Hours_Per_Day`, `Sleep_Hours_Per_Day`, `Social_Hours_Per_Day`, `Physical_Activity_Hours_Per_Day`, `GPA`, `Stress_Level` (Low / Moderate / High)
- Type: quantitative continuous (hours, GPA) + ordinal categorical (stress)
- Known caveats to document: data appears synthetic/self-reported, no collection method stated, daily hours seem to sum to ~24 (compositional constraint).

---

## Shared Data Preparation (`src/prepare_data.py`) – agree on this first
- Load raw CSV, check missing values, duplicates, impossible values, and whether hours sum to 24.
- Encode `Stress_Level` as ordinal (Low=1, Moderate=2, High=3) and keep the text label.
- Create **shared grouping columns** so every teammate uses identical definitions:
  - `social_group`, `extracurricular_group`: Low / Medium / High (tertiles)
  - `sleep_group`: Short / Normal / Long (fixed thresholds, e.g. <6, 6–8, >8 h)
  - `activity_group`: Low / Medium / High (tertiles)
  - `gpa_band`: e.g. <3.0, 3.0–3.5, >3.5
- Save `data/processed/student_lifestyle_clean.csv`.

---

## Teammate 1: Study Habits & Academic Performance (GPA vs. Study Hours)
**Question:** Does more daily study time predict a higher GPA?
**H0:** ρ = 0 (no linear relationship) / slope β₁ = 0. **H1:** ρ ≠ 0.

* **Python (`study_descriptive.ipynb`):**
  * Whole-dataset summary table (n, mean, median, mode, SD, variance, min/max, quartiles, IQR, skewness, kurtosis) for all numeric variables
  * Histograms (with normal curve) and boxplots for study hours and GPA; scatter plot study hours vs GPA
  * Correlation heatmap of all numeric variables (shared overview slide)
* **MATLAB/Octave (`study_inference.m`):**
  * Normality checks (Lilliefors / Q-Q plot)
  * Pearson and Spearman correlation with p-values and 95% CI
  * Simple linear regression GPA ~ study hours: slope, intercept, R², F-test, 95% CI for slope, residual diagnostics
  * 95% CI for mean GPA and mean study hours
  * *Optional:* multiple regression adding sleep/stress as controls (check multicollinearity)
  * Interpret: effect size in plain words ("each extra hour ≈ +X GPA points")

## Teammate 2: Health & Well-being (Sleep, Physical Activity & Stress Level)
**Question:** Do students with different stress levels differ in sleep and physical activity? Are sleep category and stress independent?
**H0:** mean sleep is equal across stress levels; sleep group and stress level are independent. **H1:** they differ / are dependent.

* **Python (`health_descriptive.ipynb`):**
  * Frequency table and bar chart for stress level (counts, %)
  * Frequency polygons of sleep hours, overlaid per stress level
  * Histograms/boxplots of sleep and physical activity by stress level
  * Contingency table sleep_group × stress_level (counts and row %)
* **MATLAB/Octave (`health_inference.m`):**
  * Assumption checks: normality per group, Levene/Bartlett for equal variances
  * One-way ANOVA (or Kruskal-Wallis if assumptions fail) for sleep across stress levels + post-hoc (`multcompare`)
  * Same for physical activity across stress levels
  * Chi-square test of independence: sleep_group × stress_level (+ Cramér's V)
  * Spearman correlation sleep vs ordinal stress
  * 95% CI for mean sleep in each stress group; interpret

## Teammate 3: Social & Extracurricular Impact (Socializing, Extracurriculars & GPA)
**Question:** Do students with high vs. low social/extracurricular activity differ in GPA?
**H0:** mean GPA is equal between groups. **H1:** it differs.

* **Python (`social_descriptive.ipynb`):**
  * Classification of students into Low/Medium/High social and extracurricular groups (class sizes table), plus a 3×3 combined classification
  * Stem-and-leaf plots of GPA for the Low and High groups (via `src/utils.py`)
  * Histograms/boxplots of GPA by group
* **MATLAB/Octave (`social_inference.m`):**
  * Welch two-sample t-test (`ttest2`) and Wilcoxon rank-sum (`ranksum`): GPA High vs Low social; same for extracurricular
  * One-way ANOVA across the 3 groups + post-hoc
  * Two-way ANOVA (`anovan`): social × extracurricular, including interaction
  * 95% CI for the difference in mean GPA, Cohen's d
  * Chi-square: group × gpa_band; interpret for the audience

---

## Joint Presentation Responsibilities
* **Objectives:** define exactly what is studied (differences, dependence, correlation) and the conclusions hoped for.
* **Data collection:** source, how collected, data type, meaning, size, caveats.
* **Synthesis:** one slide combining the three findings (which habit matters most?).
* **Conclusions:** summary, final conclusions, ideas for the future (all three).
* **SWOT:** joint analysis of the dataset and analytical approach, closes the presentation.

---

## Project Structure

```
student-lifestyle-analysis/
├── README.md                       # How to run, team roles, software versions
├── requirements.txt                # pandas, numpy, matplotlib, seaborn, scipy, jupyter, nbconvert
├── .gitignore
├── run_all.py                      # prepare data -> notebooks -> MATLAB/Octave (skips if missing)
├── data/
│   ├── raw/student_lifestyle_raw.csv        # Original Kaggle download (never edited)
│   ├── processed/student_lifestyle_clean.csv# Generated by src/prepare_data.py
│   └── data_dictionary.md                   # Each variable, unit, type, range
├── src/
│   ├── prepare_data.py             # Shared cleaning, encoding, group definitions
│   └── utils.py                    # Plot style, save_fig(), stem_and_leaf(), summary_table()
├── teammate1_study/
│   ├── study_descriptive.ipynb     # Python: summary stats, histograms, boxplots, heatmap
│   └── study_inference.m           # MATLAB/Octave: correlation, regression, CI
├── teammate2_health/
│   ├── health_descriptive.ipynb    # Python: frequency polygons, tables, crosstabs
│   └── health_inference.m          # MATLAB/Octave: ANOVA/Kruskal, chi-square
├── teammate3_social/
│   ├── social_descriptive.ipynb    # Python: classifications, stem-and-leaf
│   └── social_inference.m          # MATLAB/Octave: t-tests, ANOVA, effect sizes
├── outputs/
│   ├── figures/                    # PNGs named t<id>_figNN_<name>.png (used in PPT)
│   ├── tables/                     # CSV summary tables from Python
│   └── results/                    # t1_results.txt, t2_results.txt, t3_results.txt (p-values, R², CIs)
└── presentation/
    ├── slides_outline.md           # Slide breakdown (see below)
    ├── swot.md                     # Joint SWOT draft
    └── final_presentation.pptx
```

## Conventions
- Significance level α = 0.05 (Bonferroni/Holm correction for multiple post-hoc tests).
- Random seed fixed wherever randomness is used.
- Each script reads only `data/processed/` and writes only to its own `outputs/` files.
- Python cross-checks one key result per teammate (e.g. `scipy.stats`) against MATLAB to validate.