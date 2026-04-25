"""
Public Budget Allocation Tool
Need-Based Resource Distribution for Government Program Officers
Built by Sherriff Abdul-Hamid

This is a redesigned version of the original Smart Resource Allocation Dashboard.
Positions the tool as a decision-support instrument for government program officers
managing SNAP, Medicaid, safety net, and social protection budget cycles.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="Public Budget Allocation Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── DESIGN TOKENS ─────────────────────────────────────────────
NAVY = "#0A1F44"
GOLD = "#C9A84C"
INK = "#1A1A1A"
BODY = "#2C3E50"
MUTED = "#6B7280"
GREY_BG = "#F5F6F8"
RED = "#C8382A"
GREEN = "#1A7A2E"
AMBER = "#B8560A"

# ── CUSTOM CSS ────────────────────────────────────────────────
st.markdown(f"""
<style>
    /* Hide Streamlit chrome for cleaner product feel */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    .main .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }}

    /* Hero banner */
    .hero {{
        background: linear-gradient(135deg, {NAVY} 0%, #152B5C 100%);
        border-left: 6px solid {GOLD};
        padding: 28px 32px;
        margin-bottom: 24px;
        border-radius: 4px;
    }}
    .hero-eyebrow {{
        color: {GOLD};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }}
    .hero-title {{
        color: white;
        font-size: 30px;
        font-weight: 700;
        line-height: 1.15;
        margin-bottom: 10px;
        font-family: Georgia, serif;
    }}
    .hero-sub {{
        color: #CADCFC;
        font-size: 15px;
        font-style: italic;
        line-height: 1.5;
    }}

    /* Section headers */
    .section-label {{
        color: {MUTED};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 6px;
        margin-top: 24px;
    }}
    .section-title {{
        color: {INK};
        font-size: 22px;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 4px;
        font-family: Georgia, serif;
    }}
    .section-sub {{
        color: {MUTED};
        font-size: 13px;
        margin-bottom: 18px;
    }}

    /* KPI cards */
    .kpi-card {{
        background: white;
        border: 1px solid #E2E6EC;
        border-left: 4px solid {NAVY};
        padding: 16px 18px;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .kpi-label {{
        color: {MUTED};
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }}
    .kpi-value {{
        color: {INK};
        font-size: 26px;
        font-weight: 700;
        line-height: 1.1;
        font-family: Georgia, serif;
    }}
    .kpi-sub {{
        color: {MUTED};
        font-size: 11px;
        margin-top: 4px;
    }}

    /* Decision brief — three panel */
    .brief-panel {{
        background: white;
        border: 1px solid #E2E6EC;
        border-radius: 4px;
        padding: 18px 20px;
        height: 100%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .brief-risk {{ border-top: 4px solid {RED}; }}
    .brief-impl {{ border-top: 4px solid {NAVY}; }}
    .brief-action {{ border-top: 4px solid {GREEN}; }}
    .brief-label {{
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }}
    .brief-label-risk {{ color: {RED}; }}
    .brief-label-impl {{ color: {NAVY}; }}
    .brief-label-action {{ color: {GREEN}; }}
    .brief-body {{
        color: {BODY};
        font-size: 13px;
        line-height: 1.55;
    }}

    /* Scope note */
    .scope-note {{
        background: #FEF9E7;
        border-left: 4px solid {GOLD};
        padding: 10px 14px;
        font-size: 12px;
        color: {BODY};
        margin: 16px 0 24px;
        border-radius: 4px;
    }}

    /* Footer byline */
    .byline {{
        border-top: 1px solid #E2E6EC;
        padding-top: 14px;
        margin-top: 40px;
        color: {MUTED};
        font-size: 11px;
        font-style: italic;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: #FAFAFA;
        border-right: 1px solid #E2E6EC;
    }}
    .sidebar-heading {{
        color: {NAVY};
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }}
    .sidebar-byline {{
        font-size: 11px;
        color: {MUTED};
        border-top: 1px solid #E2E6EC;
        padding-top: 12px;
        margin-top: 20px;
    }}
    .sidebar-byline strong {{ color: {INK}; }}
</style>
""", unsafe_allow_html=True)

# ── SAMPLE DATA (US-flavored regions to signal domestic deployability) ─
DEFAULT_REGIONS = pd.DataFrame([
    {"Region": "District A — Urban Core",       "Need Score": 91, "Population":  670_000, "Poverty Rate (%)": 39.0},
    {"Region": "District B — Northern Delta",   "Need Score": 88, "Population": 1_240_000, "Poverty Rate (%)": 34.0},
    {"Region": "District C — Central Highlands","Need Score": 72, "Population":   890_000, "Poverty Rate (%)": 28.0},
    {"Region": "District D — Western Plateau",  "Need Score": 63, "Population":   510_000, "Poverty Rate (%)": 22.0},
    {"Region": "District E — Coastal Metro",    "Need Score": 54, "Population": 2_100_000, "Poverty Rate (%)": 17.0},
    {"Region": "District F — Capital Ring",     "Need Score": 41, "Population": 3_400_000, "Poverty Rate (%)": 12.0},
])

# ── SIDEBAR ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-heading">Budget Inputs</div>', unsafe_allow_html=True)

    budget_m = st.slider(
        "Total budget to allocate (US$ millions)",
        min_value=10.0, max_value=500.0, value=120.0, step=5.0,
        help="Total envelope available for distribution across regions this cycle."
    )

    st.markdown("---")
    st.markdown('<div class="sidebar-heading">Focus Region</div>', unsafe_allow_html=True)

    focus_region = st.selectbox(
        "Region to highlight in the brief",
        options=DEFAULT_REGIONS["Region"].tolist(),
        index=1,
        help="Select which region receives a dedicated briefing panel below."
    )

    st.markdown("---")
    st.markdown('<div class="sidebar-heading">Data Source</div>', unsafe_allow_html=True)
    with st.expander("View sample region dataset"):
        st.dataframe(DEFAULT_REGIONS, hide_index=True, use_container_width=True)

    st.markdown("""
    <div class="sidebar-byline">
    <strong>Built by Sherriff Abdul-Hamid</strong><br>
    Product leader specializing in government digital
    services and safety net benefits delivery.<br><br>
    USAID · UNDP · UKAID · Obama Foundation Leader
    </div>
    """, unsafe_allow_html=True)

# ── MAIN CONTENT ───────────────────────────────────────────────

# HERO BANNER
st.markdown(f"""
<div class="hero">
    <div class="hero-eyebrow">Public Budget Allocation · Decision Support Tool</div>
    <div class="hero-title">How do you distribute a limited budget fairly<br>across regions with unequal need?</div>
    <div class="hero-sub">
    A decision-support tool for program officers and policy teams managing
    safety net, Medicaid, SNAP, and social protection budget cycles.
    Generates a structured ministerial brief with risk flags and immediate action steps.
    </div>
</div>
""", unsafe_allow_html=True)

# SCOPE NOTE
st.markdown("""
<div class="scope-note">
<strong>Scope note:</strong> All figures shown are illustrative sample data for
demonstration. Production deployment requires integration with official census
data, program enrollment records, and legal/budget review procedures.
</div>
""", unsafe_allow_html=True)

# ── CORE CALCULATIONS ─────────────────────────────────────────
df = DEFAULT_REGIONS.copy()
budget = budget_m * 1_000_000

total_need = df["Need Score"].sum()
if total_need > 0:
    df["Share"] = df["Need Score"] / total_need
else:
    df["Share"] = 1 / len(df)  # fallback: equal shares

df["Allocation"] = df["Share"] * budget
df = df.sort_values("Need Score", ascending=False).reset_index(drop=True)
df.insert(0, "Rank", df.index + 1)

# Priority band
def band(score):
    if score >= 80: return ("High",   RED)
    if score >= 60: return ("Medium", AMBER)
    return            ("Low",    GREEN)

df["Priority"]      = df["Need Score"].apply(lambda s: band(s)[0])
df["Priority_Color"] = df["Need Score"].apply(lambda s: band(s)[1])

# KPIs
high_priority = df[df["Priority"] == "High"]
n_high = len(high_priority)
high_share = high_priority["Allocation"].sum() / budget * 100 if budget else 0
top_region = df.iloc[0]
top_share_pct = top_region["Allocation"] / budget * 100

# ── KEY INDICATORS ROW ────────────────────────────────────────
st.markdown('<div class="section-label">Key Indicators</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Allocation Summary</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Budget distribution, priority concentration, and top need region.</div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Envelope</div>
        <div class="kpi-value">${budget_m:.0f}M</div>
        <div class="kpi-sub">Allocated across {len(df)} regions</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: {RED};">
        <div class="kpi-label">High-Priority Regions</div>
        <div class="kpi-value">{n_high}</div>
        <div class="kpi-sub">Need score ≥ 80</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: {GOLD};">
        <div class="kpi-label">High-Priority Share</div>
        <div class="kpi-value">{high_share:.1f}%</div>
        <div class="kpi-sub">Of total budget envelope</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    top_name = top_region["Region"].split("—")[0].strip()
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: {GREEN};">
        <div class="kpi-label">Top Need Region</div>
        <div class="kpi-value" style="font-size: 17px; line-height: 1.3;">{top_name}</div>
        <div class="kpi-sub">{top_share_pct:.1f}% of envelope</div>
    </div>
    """, unsafe_allow_html=True)

# ── MINISTERIAL BRIEF ─────────────────────────────────────────
st.markdown('<div class="section-label">Decision Brief</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Risk · Implication · Action</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Structured decision summary for executive and program review.</div>', unsafe_allow_html=True)

top2_share = df.head(2)["Allocation"].sum() / budget * 100
top3_avg_poverty = df.head(3)["Poverty Rate (%)"].mean()

b1, b2, b3 = st.columns(3)

with b1:
    st.markdown(f"""
    <div class="brief-panel brief-risk">
        <div class="brief-label brief-label-risk">Risk</div>
        <div class="brief-body">
        Budget concentration risk is <strong>elevated</strong>: {high_share:.1f}% of the ${budget_m:.0f}M envelope
        flows to {n_high} high-priority regions. The top two regions absorb {top2_share:.1f}% combined —
        creating delivery dependency on a narrow set of implementation teams.
        </div>
    </div>
    """, unsafe_allow_html=True)

with b2:
    st.markdown(f"""
    <div class="brief-panel brief-impl">
        <div class="brief-label brief-label-impl">Implication</div>
        <div class="brief-body">
        The allocation is strongly targeted toward need, which improves mortality and
        hardship impact per dollar. However, {top_region['Region'].split('—')[0].strip()} alone receives
        {top_share_pct:.1f}% of the envelope, while top-3 average poverty remains at {top3_avg_poverty:.1f}% —
        signalling sustained vulnerability even after allocation.
        </div>
    </div>
    """, unsafe_allow_html=True)

with b3:
    st.markdown(f"""
    <div class="brief-panel brief-action">
        <div class="brief-label brief-label-action">Action Now</div>
        <div class="brief-body">
        Validate whether high-priority regions have sufficient delivery capacity;
        tighten monthly implementation tracking in top-funded areas;
        link disbursements to measurable poverty-reduction milestones.
        Schedule a 30-day review of concentration risk.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── FOCUS REGION BRIEF ────────────────────────────────────────
st.markdown('<div class="section-label">Focus Region</div>', unsafe_allow_html=True)
st.markdown(f'<div class="section-title">{focus_region}</div>', unsafe_allow_html=True)

focus_row = df[df["Region"] == focus_region].iloc[0]
focus_alloc = focus_row["Allocation"]
focus_share_pct = focus_alloc / budget * 100

median_need = df["Need Score"].median()
median_poverty = df["Poverty Rate (%)"].median()
median_share = df["Share"].median()

f1, f2 = st.columns(2)
with f1:
    st.markdown(f"""
    <div class="brief-panel" style="border-top: 4px solid {NAVY};">
        <div class="brief-label brief-label-impl">Why this region is positioned this way</div>
        <div class="brief-body">
        <strong>Need score:</strong> {focus_row['Need Score']} ({'above' if focus_row['Need Score'] > median_need else 'below'} regional midpoint of {median_need:.0f})<br>
        <strong>Poverty rate:</strong> {focus_row['Poverty Rate (%)']:.1f}% ({'above' if focus_row['Poverty Rate (%)'] > median_poverty else 'below'} regional midpoint of {median_poverty:.1f}%)<br>
        <strong>Population covered:</strong> {focus_row['Population']:,.0f}<br>
        <strong>Budget share:</strong> {focus_share_pct:.2f}% (${focus_alloc/1e6:.1f}M)<br>
        <strong>Priority band:</strong> {focus_row['Priority']}
        </div>
    </div>
    """, unsafe_allow_html=True)

with f2:
    recs = {
        "High": "Prioritize immediate service continuity, strengthen delivery capacity, and monitor monthly execution risks. Deploy surge support if implementation falls behind schedule.",
        "Medium": "Maintain service consistency, expand eligibility outreach to reach underserved populations within the region, and pilot targeted interventions in highest-need sub-areas.",
        "Low": "Sustain baseline operations and invest in long-term infrastructure. Monitor for emerging need signals that may trigger priority-tier reclassification in future cycles.",
    }
    st.markdown(f"""
    <div class="brief-panel" style="border-top: 4px solid {GOLD};">
        <div class="brief-label" style="color: {GOLD};">Recommendation for this region</div>
        <div class="brief-body">{recs[focus_row['Priority']]}</div>
    </div>
    """, unsafe_allow_html=True)

# ── ALLOCATION TABLE + CHART ──────────────────────────────────
st.markdown('<div class="section-label">Allocation & Ranking</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Budget Distribution by Region</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Allocations follow <code>need_score ÷ sum(need_score)</code>. If all need scores are zero, the model falls back to equal shares.</div>', unsafe_allow_html=True)

c1, c2 = st.columns([1, 1])

with c1:
    display_df = df[["Rank", "Region", "Priority", "Need Score", "Population", "Poverty Rate (%)", "Allocation"]].copy()
    display_df["Population"] = display_df["Population"].apply(lambda x: f"{x:,.0f}")
    display_df["Allocation"] = display_df["Allocation"].apply(lambda x: f"${x/1e6:.1f}M")
    display_df["Poverty Rate (%)"] = display_df["Poverty Rate (%)"].apply(lambda x: f"{x:.1f}%")

    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Rank": st.column_config.NumberColumn(width="small"),
            "Priority": st.column_config.TextColumn(width="small"),
            "Need Score": st.column_config.NumberColumn(format="%d"),
        }
    )

with c2:
    fig = go.Figure()

    df_chart = df.sort_values("Allocation", ascending=True)
    colors = [band(s)[1] for s in df_chart["Need Score"]]

    fig.add_trace(go.Bar(
        y=df_chart["Region"].str.split("—").str[0].str.strip(),
        x=df_chart["Allocation"] / 1e6,
        orientation='h',
        marker=dict(color=colors, line=dict(color='rgba(0,0,0,0)')),
        text=[f"${v/1e6:.1f}M" for v in df_chart["Allocation"]],
        textposition='outside',
        textfont=dict(size=11, color=INK, family='Calibri, sans-serif'),
        hovertemplate='<b>%{y}</b><br>Allocation: $%{x:.1f}M<extra></extra>',
    ))

    fig.update_layout(
        height=340,
        margin=dict(l=0, r=20, t=10, b=40),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            title=dict(text='Allocation (US$ millions)', font=dict(size=11, color=MUTED)),
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='#DDD8CC',
            tickfont=dict(size=10, color=BODY),
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=11, color=INK),
        ),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)

# ── EXPORT SECTION ────────────────────────────────────────────
st.markdown('<div class="section-label">Export & Share</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Download the Decision Brief</div>', unsafe_allow_html=True)

col_a, col_b = st.columns([1, 3])
with col_a:
    csv_data = df[["Rank", "Region", "Priority", "Need Score", "Population", "Poverty Rate (%)", "Allocation"]].to_csv(index=False)
    st.download_button(
        "📥 Download CSV (full allocation)",
        data=csv_data,
        file_name="budget_allocation.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col_b:
    st.markdown(f"""
    <div style="padding-top: 6px; color: {MUTED}; font-size: 12px;">
    Download the full allocation table for inclusion in ministerial briefs, budget
    hearings, or program planning documents. For PDF ministerial-brief export, connect to
    organisational reporting infrastructure.
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="byline">
<strong>Built by Sherriff Abdul-Hamid</strong> — Product leader specializing in
government digital services, safety net benefits delivery, and data-driven
resource allocation decisions. Former Founder & CEO of Poverty 360 (25,000+
beneficiaries served in West Africa). Obama Foundation Leaders Award · Mandela
Washington Fellow · Harvard Business School.<br><br>
<em>This tool is a demonstration of product design thinking for public-sector
budget allocation. All data shown is illustrative. Production deployment requires
integration with official data sources and legal review.</em><br><br>
View other projects: <a href="https://www.linkedin.com/in/abdul-hamid-sherriff-08583354/">LinkedIn</a>
</div>
""", unsafe_allow_html=True)
