# Public Budget Allocation Tool
### Need-Based Resource Distribution for Government Program Officers

**Built by Sherriff Abdul-Hamid**  
Product leader specializing in government digital services, safety net benefits delivery,  
and data-driven resource allocation decisions for public-sector programs.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://smart-resource-allocation-dashboard-eudzw5r2f9pbu4qyw3psez.streamlit.app/)

---

## The Problem This Solves

> *How do you distribute a limited budget fairly across regions with unequal need — when every allocation decision affects real people?*

Public leaders, program officers, and policy teams managing SNAP, Medicaid, housing, and social protection budget cycles face a recurring challenge: they must distribute constrained resources across regions with deeply unequal need, while balancing delivery risk, fairness, and measurable impact. This tool gives them a structured, evidence-based framework to make — and defend — those decisions.

---

## What This Tool Produces

| Output | Description |
|---|---|
| **Executive KPI Summary** | Total envelope, high-priority region count, budget concentration share, top need region |
| **Ministerial Decision Brief** | Structured three-part summary: Risk · Implication · Action Now |
| **Focus Region Brief** | Dynamic positioning rationale and recommendation for any selected region |
| **Ranked Allocation Table** | All regions ranked by need score with priority bands and dollar allocations |
| **Allocation Chart** | Need-score-weighted bar chart with priority band color coding |
| **CSV Export** | Full allocation table for inclusion in budget documents and briefing packs |

---

## Allocation Method
allocation = total_budget × (need_score ÷ sum(all_need_scores))    
- **Primary driver:** `need_score` — a composite indicator of relative regional need
- **Contextual signals:** `population` and `poverty_rate` inform the decision brief and recommendations but do not directly modify the split formula in this version
- **Fallback rule:** If all `need_score` values are zero, the model falls back to equal shares across all regions (last-resort fairness rule)
- **Priority bands:** High (score ≥ 80) · Medium (60–79) · Low (< 60)

---

## Input Data Fields

Each region record requires:

| Field | Type | Description |
|---|---|---|
| `region` | string | Region name or identifier |
| `need_score` | integer (0–100) | Composite need index — primary allocation driver |
| `population` | integer | Total population of the region |
| `poverty_rate` | float | Poverty rate as a percentage (0–100) |

---

## Repository Structure
├── app.py                  # Streamlit UI, layout, and policy messaging
├── allocation.py           # Core allocation logic and priority band ranking
├── data.py                 # Illustrative sample region dataset
├── requirements.txt        # Runtime dependencies
└── README.md               # This file

---

## Run Locally

```bash
# Clone the repository
git clone https://github.com/S-ABDUL-AI/SMART-RESOURCE-ALLOCATION-DASHBOARD.git
cd SMART-RESOURCE-ALLOCATION-DASHBOARD

# Install dependencies
pip install -r requirements.txt

# Launch the app
streamlit run app.py
```

**Requirements:** `streamlit` · `pandas` · `numpy` · `plotly`

---

## Deployment

This app is deployed on Streamlit Community Cloud.  
Live demo: [public-budget-allocation-tool.streamlit.app](https://smart-resource-allocation-dashboard-eudzw5r2f9pbu4qyw3psez.streamlit.app/)

---

## Scope Note

> All data shown in this application is **illustrative sample data** for design demonstration and policy exploration purposes.  
> Any real budget allocation decision must be paired with official census data, program enrollment records, legal budget procedures, and cabinet review processes.  
> This tool is designed to support — not replace — government decision-making.

---

## About the Author

**Sherriff Abdul-Hamid** is a product leader and data scientist specializing in government digital services, safety net benefits delivery, and decision-support tools for underserved communities.

- Former Founder & CEO, Poverty 360 — 25,000+ beneficiaries served across West Africa
- Partnered with Ghana's National Health Insurance Authority to enroll 1,250 vulnerable individuals into national health coverage
- Resource allocation decisions across USAID, UNDP, and UKAID-funded programs
- **Obama Foundation Leaders Award** — Top 1.3% globally, 2023
- **Mandela Washington Fellow** — Top 0.3%, U.S. Department of State, 2018
- Harvard Business School · Senior Executive Program

**Connect:** [LinkedIn](https://www.linkedin.com/in/abdul-hamid-sherriff-08583354/) · [Portfolio](https://share.streamlit.io/user/s-abdul-ai)

---

## Related Projects

| Project | Description |
|---|---|
| [GovFund Allocation Engine](https://impact-allocation-engine-ahxxrbgwmvyapwmifahk2b.streamlit.app) | Cost-effectiveness decision tool for public health funders — models cost-per-life-saved across malaria, nutrition, and social protection interventions |
| [Community Vulnerability Index](https://povertyearlywarningsystem-7rrmkktbi7bwha2nna8gk7.streamlit.app) | Predictive safety net targeting — identifies communities at highest risk for proactive SNAP and Medicaid outreach |
| [Global Vaccination Coverage Explorer](https://worldvaccinationcoverage-etl-ftvwbikifyyx78xyy2j3zv.streamlit.app) | WHO vaccination coverage data across 190+ countries — automated ETL pipeline for public health program managers |
