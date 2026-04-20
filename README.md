# Healthcare Access Risk Dashboard

Production-quality Streamlit dashboard to help policymakers identify U.S. states at risk of losing healthcare access.

Designed by: Sherriff Abdul-Hamid

## Challenge / Problem Statement

Spot states under pressure on healthcare access, then act on coverage, subsidies, and rural services.  
Each score blends income, insurance gaps, cost signals, and rural share.

## What This App Does

- Loads real public U.S. data (hosted CSV) and derives healthcare-style indicators by state.
- Falls back safely to simulated/sample data if real data fails.
- Trains a `RandomForestClassifier` to classify `Low`, `Medium`, and `High` risk.
- Displays policy-focused outputs:
  - Focus-state recommendation (human-style, state-specific)
  - Plain-English explanation for risk level
  - Policy brief
  - Risk chart by state
  - Feature importance chart

## Project Structure

- `app.py` - Streamlit UI and orchestration.
- `config.py` - constants (dataset URL, feature columns, random seed).
- `data.py` - loading, cleaning, validation, fallback logic.
- `modeling.py` - risk scoring, labels, model training and prediction.
- `policy.py` - recommendation engine, policy explanation, policy brief.
- `requirements.txt` - Python dependencies.

## Install and Run

```bash
cd healthcare_access_risk_dashboard
pip install -r requirements.txt
streamlit run app.py
```

## Data Source

Primary public URL:

`https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv`

Note: this source is not native healthcare data. The app transparently derives indicator-style healthcare variables from the public state-level file to keep the workflow reproducible.

## Real-World Robustness (What Was Added)

### 1) Data validation and cleaning (`data.py`)

- `clean_panel(df)` standardizes, validates, and sanitizes input:
  - normalizes column names
  - enforces required columns
  - coerces numeric types
  - clips outliers to realistic ranges
  - removes bad/duplicate state rows
  - imputes missing values using medians or safe defaults
- `is_valid_panel(df)` checks minimum viability and schema.
- `ensure_usable_panel(df)` guarantees a usable panel with layered fallback:
  1. cleaned input
  2. synthetic panel
  3. minimal hard fallback panel

### 2) Model hardening (`modeling.py`)

- `risk_scores_to_labels(scores)` now handles edge cases:
  - very small datasets
  - nearly constant scores
- `train_risk_classifier(df)` guards against training on too-few rows.
- split logic already falls back from stratified to non-stratified where needed.

### 3) App-level fault tolerance (`app.py`)

- loading path is protected by try/except and validation gates.
- model run is protected with fallback retraining on safe data.
- table/chart rendering is isolated with local fallback warnings.
- top-level app entry has a final exception guard so the Streamlit session does not fail silently.

## Input Schema

Expected modeling columns:

- `state`
- `median_income`
- `uninsured_rate`
- `healthcare_cost_index`
- `rural_population`

## Risk Logic

Composite score (0-100), where higher = higher risk:

- + Higher `uninsured_rate`
- + Higher `healthcare_cost_index`
- + Lower `median_income`
- + Higher `rural_population`

Risk classes are generated as `Low` / `Medium` / `High` bands.

## Policy Layer

- Tier baseline guidance:
  - High -> Expand Medicaid, increase subsidies, invest in rural clinics
  - Medium -> Improve insurance coverage and affordability
  - Low -> Maintain and monitor access
- Focus-state recommendation is rewritten dynamically based on state conditions.
- "Why this priority level" explains the state relative to panel medians in plain English.

## Line-by-Line Code Walkthrough (Execution Order)

This section explains the code flow in the same order the app runs.

### `app.py`

1. Import dependencies (`streamlit`, `pandas`, `plotly`, local modules).
2. Define helper `_focus_insight_for_row(...)` to generate the focus-state "why" text from the selected row.
3. Define helper `_focus_recommendation_for_row(...)` to generate state-specific recommendation text.
4. Define display mappings:
   - chart labels (`CHART_FEATURE_LABELS`)
   - tier color palette (`TIER_COLORS`)
5. Define `load_dataset_cached(...)` with `@st.cache_data`:
   - reads real vs sample mode
   - catches load failures
   - validates data
   - returns `(df, source_tag, warning_message)`
6. Define `_inject_styles()` for visual layout and callout boxes.
7. In `main()`, set page config and inject styles.
8. Render title and challenge/problem statement.
9. Build sidebar controls:
   - real/sample toggle
   - focus state selector
   - public data URL
   - attribution text
10. Show data-source warnings/messages in main panel.
11. Re-validate panel through `ensure_usable_panel`.
12. Compute row count + source label and display summary caption.
13. Train model inside guarded try/except; fallback to safe datasets on error.
14. Build `display_df` with:
   - risk scores
   - predicted tier
   - recommendation
   - priority label
15. Attach medians and compute policy insight column.
16. Compute headline metrics (`high_ct`, `mean_risk`).
17. Resolve selected focus-state row safely.
18. Determine tier style colors and generate focus recommendation.
19. Render hero section:
   - state + tier pill
   - colored risk score
   - average score
   - suggested direction (tier-colored text box)
   - why text (tier-colored text box)
20. Render panel snapshot metrics.
21. Render policy brief inside expander.
22. Render data preview and "About the numbers".
23. Render state-by-state results table.
24. Render risk bar chart and feature-importance chart.
25. Execute `main()` in top-level guarded try/except.
26. Show clear Streamlit error message if an unexpected exception escapes.

### `data.py`

1. Define required schema and numeric bounds.
2. `clean_panel(...)` sanitizes and stabilizes raw data.
3. `is_valid_panel(...)` validates cleaned panel.
4. `minimal_fallback_panel()` returns safe emergency rows.
5. `ensure_usable_panel(...)` enforces multi-layer fallback.
6. `generate_synthetic_state_data(...)` creates deterministic sample data.
7. `exports_to_healthcare_indicators(...)` transforms public CSV into modeling columns.
8. `fetch_public_dataset(...)` attempts real load and falls back safely.

### `modeling.py`

1. `compute_risk_score(...)` computes weighted normalized score.
2. `risk_scores_to_labels(...)` creates robust class labels.
3. `train_risk_classifier(...)` trains and evaluates random forest.
4. `predict_for_dataframe(...)` predicts class on full panel.

### `policy.py`

1. `recommendation_for_tier(...)` gives baseline action by tier.
2. `focus_recommendation_row(...)` generates human-style state recommendation.
3. `policy_insight_row(...)` builds state-specific explanation.
4. `attach_panel_medians(...)` creates comparison baselines.
5. `policy_brief(...)` auto-generates 3-4 sentence summary.

## Deployment Notes

### Streamlit Community Cloud

- Set entrypoint to `healthcare_access_risk_dashboard/app.py`.
- Ensure `requirements.txt` is in the same directory as entrypoint or configured correctly.
- App is resilient to temporary data URL failures (automatic sample fallback).

### Local/Server Best Practices

- Run behind a process manager (e.g., `systemd` or Docker restart policy).
- Pin dependency versions in production lockfiles.
- Add application logging and monitoring for request/data failures.

## Limitations and Next Improvements

- Current "real data" source is a public proxy input transformed to healthcare-like indicators.
- For policy production, replace transforms with direct CMS/Census/ACS health-access feeds.
- Add automated tests (`pytest`) for validation, model edge cases, and UI data contracts.

