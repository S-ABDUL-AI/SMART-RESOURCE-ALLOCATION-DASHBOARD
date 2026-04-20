# Smart Resource Allocation Dashboard

Professional Streamlit dashboard to support budget allocation decisions across regions using a transparent need-score rule.

Designed by: Sherriff Abdul-Hamid

## Problem Statement

Public leaders must distribute a limited budget across regions with unequal need, while balancing fairness, impact, and delivery risk under resource constraints.

## What This App Provides

- Executive KPI summary for the current budget scenario
- Ministerial brief in three parts: **Risk**, **Implication**, and **Action now**
- Focus-region brief that updates from sidebar selection
- Ranked allocation table with priority bands (`Low`/`Medium`/`High`)
- Allocation-by-region chart
- Policy-style recommendation notes for top regions

## Method (Current Version)

- Allocation rule: `budget × (need_score / sum(need_score))`
- If every `need_score` is zero, allocation falls back to equal shares
- `population` and `poverty_rate` are contextual in this version (not direct drivers of the split formula)

## Repository Structure

- `app.py` — Streamlit UI and policy messaging
- `allocation.py` — core allocation and ranking logic
- `data.py` — illustrative sample region data
- `requirements.txt` — runtime dependencies

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Input Data Fields

Each region row includes:

- `region`
- `need_score`
- `population`
- `poverty_rate`

## Scope Note

Data in this repository is illustrative for policy exploration and UI demonstration.  
Use official government statistics and legal budget procedures for real allocation decisions.
