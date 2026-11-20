# PPT Slide Breakdown – Statistical Analysis of Student Lifestyle

Target: ~18 slides (~15–20 min). Each slide carries a small tag showing the professor's section (1–6) so the rubric is visibly covered.

## Section 1 – Title

**Slide 1 – Title & problem statement** *(All)*
Project title, team names, course. One sentence on the problem: do daily habits affect GPA and stress?

**Slide 2 – Background: history, what is known and what is not** *(All)*
Short history of research on student habits and performance (study time, sleep, stress). What studies already show (cite 2–3 papers) vs. open questions this project tests on this dataset.

## Section 2 – Objectives

**Slide 3 – Objectives and hypotheses** *(All)*
What is studied: correlation (study vs GPA), differences (sleep across stress levels, GPA across social groups), dependence/independence (sleep group vs stress). Hoped-for conclusions. Table with 3 research questions and H0/H1.

## Section 3 – Data Collection

**Slide 4 – The dataset** *(All)*
Source (Kaggle), how collected (state honestly if unknown/likely synthetic), size (n rows, variables), variable table with type (continuous / ordinal) and meaning.

**Slide 5 – Data preparation and analysis pipeline** *(Shared)*
Cleaning checks (missing, duplicates, 24-hour check), encoding, group definitions (tertiles, sleep categories). Simple flow diagram: Python descriptive → MATLAB inference → conclusions.

## Section 4 – Descriptive Statistics

**Slide 6 – Dataset overview** *(Teammate 1)*
Summary table (mean, median, SD, IQR, skewness) for all variables and a correlation heatmap that previews the story.

**Slide 7 – Study hours and GPA: descriptive** *(Teammate 1)*
Histograms and boxplots of study hours and GPA, scatter plot. Comment on shape, spread, outliers.

**Slide 8 – Sleep, activity and stress: descriptive** *(Teammate 2)*
Stress frequency table/bar chart, frequency polygons of sleep by stress level, contingency table sleep group × stress.

**Slide 9 – Social and extracurricular activity: descriptive** *(Teammate 3)*
Classification into Low/Medium/High groups (class sizes), stem-and-leaf plots of GPA for low vs high groups, boxplots by group.

## Section 5 – Inferences

**Slide 10 – Methods overview** *(All, quick)*
One table: question → method → why chosen (correlation, regression, ANOVA/Kruskal, chi-square, t-test, CIs), α = 0.05, assumption checks.

**Slide 11 – Study hours vs GPA: results** *(Teammate 1)*
Pearson/Spearman r with CI, regression line, slope with 95% CI, R², residual check. Plain-language interpretation.

**Slide 12 – Sleep, activity and stress: results** *(Teammate 2)*
ANOVA/Kruskal-Wallis with post-hoc, chi-square independence test with Cramér's V, CIs for group means. Interpretation: does sleep differ with stress?

**Slide 13 – Social/extracurricular vs GPA: results** *(Teammate 3)*
t-test / rank-sum for High vs Low, two-way ANOVA with interaction, CI for the GPA difference, Cohen's d. Interpretation: statistically significant vs practically meaningful.

**Slide 14 – Putting it together** *(All)*
One summary visual (table or ranked effect sizes): which habit is most strongly associated with GPA and stress? Note the 24-hour trade-off between habits.

## Section 6 – Conclusions

**Slide 15 – Summary and conclusions** *(All)*
Answers to the three research questions, each with one key number, and whether the initial hopes were confirmed. Note: association, not causation.

**Slide 16 – Ideas for the future** *(All)*
Real survey data, longitudinal tracking, more variables (workload, major, income), multiple regression/ordinal logistic for stress, causal designs.

**Slide 17 – SWOT analysis** *(All)*
2×2 grid. Example content:
- Strengths: clean data, large n, mix of methods, Python + MATLAB cross-validation
- Weaknesses: likely synthetic/self-reported data, no collection method, only daily averages, hours sum to 24
- Opportunities: extend with real data, add predictive models
- Threats: misleading conclusions from correlation, ignoring confounders, data-source trust

**Slide 18 – Thank you / Q&A** *(All)*
Contact or repo link, key takeaway in one sentence.

## Backup slides (not presented unless asked)
- B1: Assumption checks (normality, variance tests, Q-Q plots)
- B2: Regression residual diagnostics
- B3: Full post-hoc tables

## Design tips
- One message per slide, with the conclusion as the slide title (e.g. "Study hours explain X% of GPA variation").
- Use the same chart style and colours from `src/utils.py` across all figures.
- Each result slide: figure on the left, 2–3 bullets of interpretation on the right.
- Put each teammate's speaker notes in `presentation/`.