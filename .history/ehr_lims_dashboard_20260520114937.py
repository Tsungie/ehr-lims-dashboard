import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components
import io, requests

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EHR–LIMS Validation",
    layout="wide",
    page_icon="🏥",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLES (Modernized)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { 
    font-family: 'Inter', sans-serif; 
    background-color: #F8FAFC;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 2rem 3rem; max-width: 1400px; }

/* ── Section headers ── */
.sec-hdr {
    font-size: 16px; font-weight: 700; color: #0F172A;
    margin: 36px 0 16px; display: flex; align-items: center; gap: 12px;
    letter-spacing: -0.3px;
}
.sec-hdr::after {
    content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, #E2E8F0, transparent);
}

/* ── Sidebar Styling ── */
[data-testid="stSidebar"] {
    background: #0B1121 !important;
    border-right: 1px solid rgba(255,255,255,0.05);
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] .stMultiSelect div,
[data-testid="stSidebar"] .stSelectbox div { 
    background: rgba(255,255,255,0.04) !important; 
    border-color: rgba(255,255,255,0.08) !important; 
    border-radius: 8px;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.08) !important; }

/* ── Drilldown Stats ── */
.drill-stat { 
    background: white; border-radius: 12px; padding: 12px 16px; 
    margin-bottom: 10px; border: 1px solid #E2E8F0; 
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.drill-stat .ds-lbl { font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;}
.drill-stat .ds-val { font-size: 18px; font-weight: 800; color: #0F172A; margin-top: 4px; letter-spacing: -0.5px;}

</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
MONTHS = ["Oct-25", "Nov-25", "Dec-25", "Jan-26", "Feb-26", "Mar-26", "Apr-26"]
MONTH_DATES = {
    "Oct-25": datetime(2025, 10, 1),
    "Nov-25": datetime(2025, 11, 1),
    "Dec-25": datetime(2025, 12, 1),
    "Jan-26": datetime(2026, 1, 1),
    "Feb-26": datetime(2026, 2, 1),
    "Mar-26": datetime(2026, 3, 1),
    "Apr-26": datetime(2026, 4, 1),
}

# ─────────────────────────────────────────────────────────────────────────────
# SHAREPOINT CONFIG
# ─────────────────────────────────────────────────────────────────────────────
SHAREPOINT_URL = (
    "https://itechzim.sharepoint.com/:x:/s/EHR-Documents/"
    "IQC7CQPdu9SIS6SYda-FfluIAd8KSi35YOs_8tXoGrLGufg?e=srcR0P&download=1"
)


# ─────────────────────────────────────────────────────────────────────────────
# DATA FETCH & PARSE
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_sharepoint(url: str) -> bytes:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*",
    }
    session = requests.Session()
    resp = session.get(url, headers=headers, allow_redirects=True, timeout=30)
    resp.raise_for_status()
    return resp.content


def parse_val(v):
    if pd.isna(v):
        return np.nan
    s = str(v).strip()
    if s in ["N/A", "", "#VALUE!", "nan", "-"]:
        return np.nan
    try:
        return float(s)
    except:
        return np.nan


@st.cache_data(show_spinner=False)
def load_data(file_bytes: bytes) -> pd.DataFrame:
    try:
        df_raw = pd.read_excel(io.BytesIO(file_bytes), header=None, dtype=str)
    except:
        df_raw = pd.read_csv(io.BytesIO(file_bytes), header=None, dtype=str)

    records = []
    for i in range(2, len(df_raw)):
        row = df_raw.iloc[i]
        district = str(row[0]).strip()
        facility = str(row[1]).strip()
        if district in ["", "nan"] or facility in ["", "nan"]:
            continue
        try:
            activation_date = pd.to_datetime(str(row[2]).strip(), dayfirst=True)
        except:
            activation_date = None
        act_month = (
            datetime(activation_date.year, activation_date.month, 1)
            if activation_date
            else None
        )

        for j, month in enumerate(MONTHS):
            if act_month and MONTH_DATES[month] <= act_month:
                continue
            records.append(
                {
                    "District": district,
                    "Facility": facility,
                    "Activation Date": activation_date,
                    "Month": month,
                    "Month Date": MONTH_DATES[month],
                    "VL Paper (BAs)": parse_val(row[3 + j]),
                    "VL LIMS": parse_val(row[10 + j]),
                    "VL EHR (BAs)": parse_val(row[17 + j]),
                    "VL SHR (Jima)": parse_val(row[24 + j]),
                }
            )

    df = pd.DataFrame(records)
    if df.empty:
        return df
    df["Gap1"] = df["VL Paper (BAs)"] - df["VL EHR (BAs)"]
    df["Gap2"] = df["VL EHR (BAs)"] - df["VL SHR (Jima)"]
    df["Gap1 %"] = np.where(
        df["VL Paper (BAs)"] > 0,
        (df["Gap1"] / df["VL Paper (BAs)"] * 100).round(1),
        np.nan,
    )
    df["Gap2 %"] = np.where(
        df["VL EHR (BAs)"] > 0, (df["Gap2"] / df["VL EHR (BAs)"] * 100).round(1), np.nan
    )
    return df


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
    <div style='padding:10px 0 20px'>
        <div style='width: 40px; height: 40px; background: linear-gradient(135deg, #3B82F6, #8B5CF6); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; margin-bottom: 12px;'>📊</div>
        <div style='font-size:20px;font-weight:800;color:white; letter-spacing: -0.5px;'>EHR–LIMS</div>
        <div style='font-size:12px;color:rgba(255,255,255,0.6);margin-top:2px; font-weight:500;'>Validation Dashboard</div>
    </div>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """<div style='display:flex;align-items:center;gap:10px;background:rgba(255,255,255,0.03);border: 1px solid rgba(255,255,255,0.05);border-radius:10px;padding:12px;margin-bottom:20px'>
            <div style='position: relative; width: 8px; height: 8px;'>
                <div style='position: absolute; width: 100%; height: 100%; background: #10B981; border-radius: 50%;'></div>
                <div style='position: absolute; width: 100%; height: 100%; background: #10B981; border-radius: 50%; animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;'></div>
            </div>
            <div>
                <div style='font-size:11px;font-weight:700;color:white;letter-spacing:0.3px;'>LIVE CONNECTION</div>
                <div style='font-size:10px;color:rgba(255,255,255,0.4);margin-top:2px'>SharePoint Auto-Sync</div>
            </div>
        </div>
        <style>@keyframes ping { 75%, 100% { transform: scale(2.5); opacity: 0; } }</style>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🔄 Refresh Data", use_container_width=True):
        fetch_sharepoint.clear()
        st.rerun()

    st.markdown("<hr style='margin: 24px 0'>", unsafe_allow_html=True)

    with st.spinner("Fetching live data..."):
        try:
            file_bytes = fetch_sharepoint(SHAREPOINT_URL)
            sp_ok = True
        except Exception as sp_err:
            sp_ok, sp_error = False, str(sp_err)

    if not sp_ok:
        st.error(f"SharePoint Error: {sp_error}")
        st.stop()

    df = load_data(file_bytes)

    districts = sorted(df["District"].unique())
    st.markdown(
        "<div style='font-size:10px;font-weight:700;color:rgba(255,255,255,0.5);letter-spacing:1px;margin-bottom:8px'>FILTER DISTRICT</div>",
        unsafe_allow_html=True,
    )
    sel_districts = st.multiselect(
        "Districts", districts, default=districts, label_visibility="collapsed"
    )

    fac_pool = sorted(df[df["District"].isin(sel_districts)]["Facility"].unique())
    st.markdown(
        "<div style='font-size:10px;font-weight:700;color:rgba(255,255,255,0.5);letter-spacing:1px;margin-top:16px;margin-bottom:8px'>FILTER FACILITY</div>",
        unsafe_allow_html=True,
    )
    sel_facilities = st.multiselect(
        "Facilities", fac_pool, default=fac_pool, label_visibility="collapsed"
    )

    st.markdown(
        "<div style='font-size:10px;font-weight:700;color:rgba(255,255,255,0.5);letter-spacing:1px;margin-top:16px;margin-bottom:8px'>TIME PERIOD</div>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        m_start = st.selectbox("From", MONTHS, index=0, label_visibility="collapsed")
    with c2:
        m_end = st.selectbox(
            "To", MONTHS, index=len(MONTHS) - 1, label_visibility="collapsed"
        )

if df.empty:
    st.error("No data parsed.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# FILTER & AGGREGATE
# ─────────────────────────────────────────────────────────────────────────────
sel_months = MONTHS[MONTHS.index(m_start) : MONTHS.index(m_end) + 1]
dff = df[
    df["District"].isin(sel_districts)
    & df["Facility"].isin(sel_facilities)
    & df["Month"].isin(sel_months)
].copy()

total_paper = dff["VL Paper (BAs)"].sum()
total_ehr = dff["VL EHR (BAs)"].sum()
total_shr = dff["VL SHR (Jima)"].sum()
gap1_tot = total_paper - total_ehr
gap2_tot = total_ehr - total_shr
gap1_pct = round(gap1_tot / total_paper * 100, 1) if total_paper > 0 else 0
gap2_pct = round(gap2_tot / total_ehr * 100, 1) if total_ehr > 0 else 0
capture_rate = round(total_ehr / total_paper * 100, 1) if total_paper > 0 else 0
submit_rate = round(total_shr / total_ehr * 100, 1) if total_ehr > 0 else 0
n_fac = dff["Facility"].nunique()

# ─────────────────────────────────────────────────────────────────────────────
# TOP SECTION — Premium Flow Component
# ─────────────────────────────────────────────────────────────────────────────
components.html(
    f"""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
* {{ box-sizing:border-box; margin:0; padding:0; font-family:'Inter',sans-serif; }}
body {{ background: transparent; padding: 10px; }}

/* ── Header ── */
.hdr {{ display:flex; justify-content:space-between; align-items:flex-end; margin-bottom: 24px; }}
.hdr-title {{ font-size: 24px; font-weight: 800; color: #0F172A; letter-spacing: -0.5px; }}
.hdr-sub {{ font-size: 13px; color: #64748B; font-weight: 500; margin-top: 4px; }}
.hdr-meta {{ display:flex; gap: 8px; margin-top: 12px; }}
.meta-tag {{ background: white; border: 1px solid #E2E8F0; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; color: #475569; box-shadow: 0 1px 2px rgba(0,0,0,0.02); }}

/* ── Process Flow ── */
.flow-wrapper {{ display: flex; align-items: center; justify-content: space-between; gap: 20px; margin-bottom: 32px; background: white; padding: 32px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.03), 0 1px 3px rgba(0,0,0,0.02); border: 1px solid #F1F5F9; }}
.flow-node {{ flex: 1; text-align: center; position: relative; }}
.flow-node::after {{ content: '➔'; position: absolute; right: -24px; top: 40%; font-size: 24px; color: #CBD5E1; z-index: 1; }}
.flow-node:last-child::after {{ display: none; }}

.node-val {{ font-size: 36px; font-weight: 800; color: #0F172A; letter-spacing: -1px; line-height: 1.1; }}
.node-lbl {{ font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #64748B; margin-top: 8px; }}
.node-sub {{ font-size: 11px; color: #94A3B8; margin-top: 2px; }}

/* Leakage Badges over arrows */
.leak-badge {{ position: absolute; right: -40px; top: -15px; background: white; border-radius: 20px; padding: 6px 12px; font-size: 11px; font-weight: 700; z-index: 10; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 1px solid #E2E8F0; display: flex; flex-direction: column; align-items: center; }}
.lb-val {{ font-size: 13px; }}
.lb-lbl {{ font-size: 9px; text-transform: uppercase; opacity: 0.8; margin-top: 2px; }}
.leak-amber {{ color: #D97706; border-color: #FDE68A; background: #FFFBEB; }}
.leak-red {{ color: #DC2626; border-color: #FECACA; background: #FEF2F2; }}

/* ── KPI Grid ── */
.kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }}
.kpi-card {{ background: white; padding: 20px; border-radius: 12px; border: 1px solid #F1F5F9; box-shadow: 0 2px 8px rgba(0,0,0,0.02); transition: transform 0.2s; position: relative; overflow: hidden; }}
.kpi-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 16px rgba(0,0,0,0.04); border-color: #E2E8F0; }}
.kpi-val {{ font-size: 28px; font-weight: 800; color: #0F172A; letter-spacing: -0.5px; }}
.kpi-lbl {{ font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #64748B; margin-top: 8px; }}

.border-green {{ border-bottom: 3px solid #10B981; }}
.border-blue {{ border-bottom: 3px solid #3B82F6; }}
.border-amber {{ border-bottom: 3px solid #F59E0B; }}
.border-red {{ border-bottom: 3px solid #EF4444; }}

</style>

<div class="hdr">
    <div>
        <div class="hdr-title">Viral Load Data Pipeline</div>
        <div class="hdr-sub">Tracking sample collection, LIMS/EHR capture, and SHR submission.</div>
        <div class="hdr-meta">
            <div class="meta-tag">🏥 {n_fac} Facilities Active</div>
            <div class="meta-tag">📅 {len(sel_months)} Months Analyzed</div>
            <div class="meta-tag">🔄 Updated: {datetime.now().strftime('%H:%M')}</div>
        </div>
    </div>
</div>

<div class="flow-wrapper">
    <div class="flow-node">
        <div class="node-val" id="n1">0</div>
        <div class="node-lbl" style="color: #0F766E;">1. Paper Collected</div>
        <div class="node-sub">Physical samples recorded</div>
        
        <div class="leak-badge leak-amber">
            <span class="lb-val">-{gap1_pct}%</span>
            <span class="lb-lbl">Leakage 1</span>
        </div>
    </div>
    
    <div class="flow-node">
        <div class="node-val" id="n2">0</div>
        <div class="node-lbl" style="color: #4338CA;">2. EHR Captured</div>
        <div class="node-sub">Successfully digitized</div>
        
        <div class="leak-badge leak-red">
            <span class="lb-val">-{gap2_pct}%</span>
            <span class="lb-lbl">Leakage 2</span>
        </div>
    </div>
    
    <div class="flow-node">
        <div class="node-val" id="n3">0</div>
        <div class="node-lbl" style="color: #6D28D9;">3. SHR Submitted</div>
        <div class="node-sub">Synced to central repo</div>
    </div>
</div>

<div class="kpi-grid">
    <div class="kpi-card border-green">
        <div class="kpi-val" id="k1">0%</div>
        <div class="kpi-lbl">Overall Capture Rate</div>
    </div>
    <div class="kpi-card border-blue">
        <div class="kpi-val" id="k2">0%</div>
        <div class="kpi-lbl">Overall Submit Rate</div>
    </div>
    <div class="kpi-card border-amber">
        <div style="font-size: 11px; color:#D97706; font-weight:700; margin-bottom:4px">GAP 1 (PAPER VS EHR)</div>
        <div class="kpi-val" id="k3">0</div>
        <div class="kpi-lbl">Samples Lost</div>
    </div>
    <div class="kpi-card border-red">
        <div style="font-size: 11px; color:#DC2626; font-weight:700; margin-bottom:4px">GAP 2 (EHR VS SHR)</div>
        <div class="kpi-val" id="k4">0</div>
        <div class="kpi-lbl">Samples Lost</div>
    </div>
</div>

<script>
function anim(id, target, isPct) {{
    const el = document.getElementById(id);
    if(!el) return;
    let start = null;
    const dur = 1000;
    function step(t) {{
        if(!start) start = t;
        const p = Math.min((t - start) / dur, 1);
        const ease = 1 - Math.pow(1 - p, 3);
        const current = ease * target;
        el.textContent = isPct ? current.toFixed(1) + '%' : Math.floor(current).toLocaleString();
        if(p < 1) requestAnimationFrame(step);
        else el.textContent = isPct ? target.toFixed(1) + '%' : target.toLocaleString();
    }}
    requestAnimationFrame(step);
}}
setTimeout(() => anim('n1', {int(total_paper)}, false), 100);
setTimeout(() => anim('n2', {int(total_ehr)}, false), 300);
setTimeout(() => anim('n3', {int(total_shr)}, false), 500);
setTimeout(() => anim('k1', {capture_rate}, true), 200);
setTimeout(() => anim('k2', {submit_rate}, true), 400);
setTimeout(() => anim('k3', {int(gap1_tot)}, false), 600);
setTimeout(() => anim('k4', {int(gap2_tot)}, false), 800);
</script>
""",
    height=440,
)

# ─────────────────────────────────────────────────────────────────────────────
# FACILITY AGGREGATES
# ─────────────────────────────────────────────────────────────────────────────
fac = dff.groupby(["District", "Facility"], as_index=False).agg(
    Paper=("VL Paper (BAs)", "sum"),
    EHR=("VL EHR (BAs)", "sum"),
    SHR=("VL SHR (Jima)", "sum"),
)
fac["Gap1"] = fac["Paper"] - fac["EHR"]
fac["Gap2"] = fac["EHR"] - fac["SHR"]
fac["Gap1 %"] = (fac["Gap1"] / fac["Paper"] * 100).round(1)
fac["Gap2 %"] = (fac["Gap2"] / fac["EHR"] * 100).round(1)

# ─────────────────────────────────────────────────────────────────────────────
# GAP CHARTS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="sec-hdr">📊 Leakage by Facility Breakdown</div>',
    unsafe_allow_html=True,
)
col_a, col_b = st.columns(2)


def styled_bar(df_in, bg_col, fg_col, bg_name, fg_name, gap_col, gap_pct_col, title):
    s = df_in.sort_values(gap_col, ascending=False)
    # Semantic Colors: Red for critical leakage, Amber for warning, Emerald for good
    colors = [
        "#F87171" if v > 30 else "#FBBF24" if v > 10 else "#34D399"
        for v in s[gap_pct_col].fillna(0)
    ]

    fig = go.Figure()
    fig.add_bar(
        y=s["Facility"],
        x=s[bg_col],
        name=bg_name,
        orientation="h",
        marker_color="#F1F5F9",
        hoverinfo="skip",
    )
    fig.add_bar(
        y=s["Facility"],
        x=s[fg_col],
        name=fg_name,
        orientation="h",
        marker_color=colors,
        hovertemplate="<b>%{y}</b><br>Captured: %{x:,}<br>Leakage: %{customdata:.1f}%<extra></extra>",
        customdata=s[gap_pct_col],
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#0F172A")),
        barmode="overlay",
        height=400,
        margin=dict(l=10, r=20, t=50, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
        xaxis=dict(
            showgrid=True, gridcolor="#F8FAFC", tickfont=dict(size=11, color="#64748B")
        ),
        yaxis=dict(tickfont=dict(size=11, color="#334155")),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


with col_a:
    st.plotly_chart(
        styled_bar(
            fac,
            "Paper",
            "EHR",
            "Total Collected (Paper)",
            "Captured (EHR)",
            "Gap1",
            "Gap1 %",
            "Gap 1 (Paper to EHR) Analysis",
        ),
        use_container_width=True,
        config={"displayModeBar": False},
    )
with col_b:
    st.plotly_chart(
        styled_bar(
            fac,
            "EHR",
            "SHR",
            "Total Captured (EHR)",
            "Submitted (SHR)",
            "Gap2",
            "Gap2 %",
            "Gap 2 (EHR to SHR) Analysis",
        ),
        use_container_width=True,
        config={"displayModeBar": False},
    )

# ─────────────────────────────────────────────────────────────────────────────
# MONTHLY TREND + DRILLDOWN
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="sec-hdr">📈 Monthly Performance & Deep Dive</div>',
    unsafe_allow_html=True,
)

col_trend, col_drill = st.columns([1.8, 1.2])

monthly = dff.groupby("Month", as_index=False).agg(
    Paper=("VL Paper (BAs)", "sum"),
    EHR=("VL EHR (BAs)", "sum"),
    SHR=("VL SHR (Jima)", "sum"),
)
monthly["Month Date"] = monthly["Month"].map(MONTH_DATES)
monthly = monthly.sort_values("Month Date")

with col_trend:
    fig_trend = go.Figure()
    # Smooth spline lines with semi-transparent area fills
    fig_trend.add_scatter(
        x=monthly["Month"],
        y=monthly["Paper"],
        name="Paper Collected",
        mode="lines+markers",
        line=dict(color="#10B981", width=3, shape="spline"),
        marker=dict(size=8, color="white", line=dict(color="#10B981", width=2)),
    )

    fig_trend.add_scatter(
        x=monthly["Month"],
        y=monthly["EHR"],
        name="EHR Captured",
        mode="lines+markers",
        line=dict(color="#3B82F6", width=3, shape="spline"),
        marker=dict(size=8, color="white", line=dict(color="#3B82F6", width=2)),
        fill="tonexty",
        fillcolor="rgba(59,130,246,0.05)",
    )

    fig_trend.add_scatter(
        x=monthly["Month"],
        y=monthly["SHR"],
        name="SHR Submitted",
        mode="lines+markers",
        line=dict(color="#8B5CF6", width=3, shape="spline"),
        marker=dict(size=8, color="white", line=dict(color="#8B5CF6", width=2)),
        fill="tonexty",
        fillcolor="rgba(139,92,246,0.05)",
    )

    fig_trend.update_layout(
        title=dict(
            text="Aggregate Volume Over Time", font=dict(size=14, color="#0F172A")
        ),
        height=380,
        margin=dict(l=10, r=10, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
        xaxis=dict(gridcolor="#F1F5F9", showgrid=False),
        yaxis=dict(gridcolor="#F1F5F9", title="Volume"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
    )
    st.plotly_chart(
        fig_trend, use_container_width=True, config={"displayModeBar": False}
    )

with col_drill:
    st.markdown(
        "<div style='margin-top: 10px; margin-bottom: 5px; font-size:12px; font-weight:700; color:#64748B;'>FACILITY SNAPSHOT</div>",
        unsafe_allow_html=True,
    )
    sel_fac = st.selectbox(
        "Facility Drilldown",
        sorted(dff["Facility"].unique()),
        label_visibility="collapsed",
    )
    fac_df = dff[dff["Facility"] == sel_fac].sort_values("Month Date")

    dist = fac_df["District"].iloc[0] if not fac_df.empty else "—"
    act = fac_df["Activation Date"].iloc[0] if not fac_df.empty else None
    g1, g2 = fac_df["Gap1"].sum(), fac_df["Gap2"].sum()

    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown(
            f"""
        <div class="drill-stat"><div class="ds-lbl">District</div><div class="ds-val">{dist}</div></div>
        <div class="drill-stat"><div class="ds-lbl">Total Gap 1</div><div class="ds-val" style="color:#D97706">{int(g1):,}</div></div>
        """,
            unsafe_allow_html=True,
        )
    with sc2:
        st.markdown(
            f"""
        <div class="drill-stat"><div class="ds-lbl">Activated</div><div class="ds-val">{act.strftime('%b %Y') if act else '—'}</div></div>
        <div class="drill-stat"><div class="ds-lbl">Total Gap 2</div><div class="ds-val" style="color:#DC2626">{int(g2):,}</div></div>
        """,
            unsafe_allow_html=True,
        )

    fig_drill = go.Figure()
    fig_drill.add_scatter(
        x=fac_df["Month"],
        y=fac_df["VL Paper (BAs)"],
        name="Paper",
        line=dict(color="#10B981", width=2),
    )
    fig_drill.add_scatter(
        x=fac_df["Month"],
        y=fac_df["VL EHR (BAs)"],
        name="EHR",
        line=dict(color="#3B82F6", width=2),
    )
    fig_drill.add_scatter(
        x=fac_df["Month"],
        y=fac_df["VL SHR (Jima)"],
        name="SHR",
        line=dict(color="#8B5CF6", width=2),
    )
    fig_drill.update_layout(
        height=170,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False,
        xaxis=dict(showgrid=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=10)),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
    )
    st.plotly_chart(
        fig_drill, use_container_width=True, config={"displayModeBar": False}
    )
