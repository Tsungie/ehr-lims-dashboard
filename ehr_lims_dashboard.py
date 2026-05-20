import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components
import io, time, requests

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EHR–LIMS Validation Dashboard",
    layout="wide",
    page_icon="🔬",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem; max-width: 1400px; }

/* ── hero banner ── */
.hero {
    background: linear-gradient(135deg, #0A1628 0%, #0F3460 55%, #16213E 100%);
    border-radius: 16px; padding: 32px 40px 28px;
    margin-bottom: 28px; color: white; position: relative; overflow: hidden;
}
.hero::before {
    content: ''; position: absolute; top: -60px; right: -60px;
    width: 280px; height: 280px; border-radius: 50%;
    background: rgba(0,180,216,0.08); pointer-events: none;
}
.hero::after {
    content: ''; position: absolute; bottom: -80px; right: 120px;
    width: 200px; height: 200px; border-radius: 50%;
    background: rgba(6,214,160,0.06); pointer-events: none;
}
.hero-title   { font-size: 26px; font-weight: 700; margin: 0 0 6px; letter-spacing: -0.3px; }
.hero-sub     { font-size: 13px; color: rgba(255,255,255,0.6); margin: 0; }
.hero-badge   {
    display: inline-block; background: rgba(6,214,160,0.2);
    color: #06D6A0; border: 1px solid rgba(6,214,160,0.4);
    border-radius: 20px; padding: 3px 12px; font-size: 11px;
    font-weight: 600; margin-top: 12px; letter-spacing: 0.3px;
}

/* ── pipeline flow ── */
.pipeline {
    display: flex; align-items: center; gap: 0;
    background: rgba(255,255,255,0.04); border-radius: 12px;
    padding: 16px 24px; margin-top: 20px; border: 1px solid rgba(255,255,255,0.08);
}
.pipe-node {
    flex: 1; text-align: center;
}
.pipe-node .pn-val  { font-size: 22px; font-weight: 700; color: white; }
.pipe-node .pn-lbl  { font-size: 11px; color: rgba(255,255,255,0.5); margin-top: 2px; }
.pipe-node .pn-sub  { font-size: 10px; color: rgba(255,255,255,0.35); }
.pipe-arrow {
    flex: 0 0 100px; display: flex; flex-direction: column;
    align-items: center; padding: 0 8px;
}
.pa-line {
    width: 100%; height: 2px; position: relative;
    background: linear-gradient(90deg, rgba(255,255,255,0.15), rgba(255,255,255,0.15));
}
.pa-line::after {
    content: '▶'; position: absolute; right: -6px; top: -8px;
    color: rgba(255,255,255,0.3); font-size: 11px;
}
.pa-gap-pill {
    font-size: 10px; font-weight: 700; border-radius: 20px;
    padding: 2px 10px; margin-bottom: 5px; letter-spacing: 0.3px;
}
.gap1-pill { background: rgba(255,183,3,0.2); color: #FFB703; border: 1px solid rgba(255,183,3,0.4); }
.gap2-pill { background: rgba(239,71,111,0.2); color: #EF476F; border: 1px solid rgba(239,71,111,0.4); }

/* ── kpi card ── */
.kpi-card {
    background: white; border-radius: 14px; padding: 20px 22px;
    border: 1px solid #E8EDF3; position: relative; overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.09); }
.kpi-card .kc-icon {
    width: 40px; height: 40px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; margin-bottom: 14px;
}
.kpi-card .kc-val  { font-size: 28px; font-weight: 700; color: #0D1B2A; letter-spacing: -0.5px; }
.kpi-card .kc-lbl  { font-size: 12px; font-weight: 600; color: #64748B; margin-top: 2px; }
.kpi-card .kc-sub  { font-size: 11px; color: #94A3B8; margin-top: 4px; }
.kpi-card .kc-bar  { position: absolute; bottom: 0; left: 0; height: 3px; border-radius: 0 0 14px 14px; }
.kc-blue   .kc-icon { background: #EFF6FF; }
.kc-green  .kc-icon { background: #F0FDF4; }
.kc-purple .kc-icon { background: #F5F3FF; }
.kc-amber  .kc-icon { background: #FFFBEB; }
.kc-red    .kc-icon { background: #FFF1F2; }
.kc-blue   .kc-bar  { background: #3B82F6; width: 100%; }
.kc-green  .kc-bar  { background: #10B981; width: 100%; }
.kc-purple .kc-bar  { background: #8B5CF6; width: 100%; }
.kc-amber  .kc-bar  { background: #F59E0B; width: 100%; }
.kc-red    .kc-bar  { background: #EF4444; width: 100%; }

/* ── section header ── */
.sec-hdr {
    font-size: 14px; font-weight: 600; color: #0D1B2A;
    margin: 28px 0 12px; display: flex; align-items: center; gap: 8px;
}
.sec-hdr::after {
    content: ''; flex: 1; height: 1px; background: #E8EDF3;
}

/* ── chart card ── */
.chart-card {
    background: white; border-radius: 14px; padding: 20px;
    border: 1px solid #E8EDF3; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* ── leaderboard ── */
.lb-row {
    display: flex; align-items: center; padding: 10px 14px;
    border-radius: 10px; margin-bottom: 6px; gap: 12px;
    background: #FAFBFC; border: 1px solid #F1F5F9; transition: background 0.15s;
}
.lb-row:hover { background: #F1F5F9; }
.lb-rank { font-size: 13px; font-weight: 700; color: #94A3B8; min-width: 22px; }
.lb-name { flex: 1; }
.lb-name .lbn-fac { font-size: 13px; font-weight: 600; color: #0D1B2A; }
.lb-name .lbn-dist { font-size: 11px; color: #94A3B8; }
.lb-bars { flex: 0 0 160px; }
.lb-badge {
    font-size: 11px; font-weight: 700; border-radius: 20px;
    padding: 2px 10px; white-space: nowrap;
}
.badge-red    { background: #FFF1F2; color: #BE123C; border: 1px solid #FECDD3; }
.badge-amber  { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
.badge-green  { background: #F0FDF4; color: #15803D; border: 1px solid #BBF7D0; }
.badge-purple { background: #F5F3FF; color: #6D28D9; border: 1px solid #DDD6FE; }

/* ── pulse animation for worst offenders ── */
@keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
    50%       { box-shadow: 0 0 0 6px rgba(239,68,68,0.15); }
}
.lb-row.critical { animation: pulse-red 2.5s ease-in-out infinite; border-color: #FECDD3; background: #FFF5F5; }

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: #0A1628 !important;
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] .stMultiSelect div,
[data-testid="stSidebar"] .stSelectbox div { background: rgba(255,255,255,0.07) !important; border-color: rgba(255,255,255,0.12) !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.1) !important; }

/* ── drilldown ── */
.drill-stat { background: #F8FAFC; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; border: 1px solid #E8EDF3; }
.drill-stat .ds-lbl { font-size: 11px; color: #94A3B8; font-weight: 500; }
.drill-stat .ds-val { font-size: 18px; font-weight: 700; color: #0D1B2A; margin-top: 2px; }
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

PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        font=dict(family="Inter, sans-serif", color="#334155"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        colorway=["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EF4444", "#06B6D4"],
    )
)


# ─────────────────────────────────────────────────────────────────────────────
# ANIMATED COUNTER COMPONENT
# ─────────────────────────────────────────────────────────────────────────────
def kpi_card(value, label, sublabel, color_class, icon, bar_color):
    """Renders an animated KPI counter card."""
    html = f"""
    <div class="kpi-card {color_class}" id="card_{label.replace(' ','')}">
        <div class="kc-icon">{icon}</div>
        <div class="kc-val" id="counter_{label.replace(' ','')}">0</div>
        <div class="kc-lbl">{label}</div>
        <div class="kc-sub">{sublabel}</div>
        <div class="kc-bar"></div>
    </div>
    <script>
    (function() {{
        const el = document.getElementById('counter_{label.replace(' ','')}');
        if (!el) return;
        const target = {int(abs(value))};
        const prefix = {'"-"' if value < 0 else '""'};
        const duration = 1200;
        const start = performance.now();
        function update(now) {{
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const ease = 1 - Math.pow(1 - progress, 3);
            el.textContent = prefix + Math.floor(ease * target).toLocaleString();
            if (progress < 1) requestAnimationFrame(update);
            else el.textContent = prefix + target.toLocaleString();
        }}
        requestAnimationFrame(update);
    }})();
    </script>
    """
    components.html(html, height=170)


# ─────────────────────────────────────────────────────────────────────────────
# SHAREPOINT CONFIG  — paste your sharing link here
# ─────────────────────────────────────────────────────────────────────────────
SHAREPOINT_URL = (
    "https://itechzim.sharepoint.com/:x:/s/EHR-Documents/"
    "IQC7CQPdu9SIS6SYda-FfluIAd8KSi35YOs_8tXoGrLGufg?e=srcR0P&download=1"
)


# ─────────────────────────────────────────────────────────────────────────────
# DATA FETCH FROM SHAREPOINT
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_sharepoint(url: str) -> bytes:
    """Download the live Excel from a SharePoint sharing link."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "application/vnd.openxmlformats-officedocument" ".spreadsheetml.sheet,*/*"
        ),
    }
    session = requests.Session()
    # Follow redirects — SharePoint sharing links redirect to the real file
    resp = session.get(url, headers=headers, allow_redirects=True, timeout=30)
    resp.raise_for_status()
    return resp.content


# ─────────────────────────────────────────────────────────────────────────────
# DATA PARSING
# ─────────────────────────────────────────────────────────────────────────────
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
    except Exception:
        df_raw = pd.read_csv(io.BytesIO(file_bytes), header=None, dtype=str)

    records = []
    for i in range(2, len(df_raw)):
        row = df_raw.iloc[i]
        district = str(row[0]).strip()
        facility = str(row[1]).strip()
        if district in ["", "nan"] or facility in ["", "nan"]:
            continue
        activation_date = None
        try:
            activation_date = pd.to_datetime(str(row[2]).strip(), dayfirst=True)
        except Exception:
            pass
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


import base64 as _b64, os as _os

_logo_path = "logo.png"
if _os.path.exists(_logo_path):
    with open(_logo_path, "rb") as _lf:
        _logo_src = "data:image/png;base64," + _b64.b64encode(_lf.read()).decode()
else:
    _logo_src = ""
# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:

    # Logo + title
    st.markdown(
        f"""
    <div style='display:flex;align-items:center;gap:10px;padding:12px 0 10px'>
        <img src='{_logo_src}' style='width:40px;height:40px;object-fit:contain;
             border-radius:8px;background:white;padding:2px;flex-shrink:0;' alt='MoHCC'/>
        <div>
            <div style='font-size:15px;font-weight:700;color:white;line-height:1.2'>EHR–LIMS</div>
            <div style='font-size:10px;color:rgba(255,255,255,0.4);margin-top:1px'>Validation Dashboard</div>
        </div>
    </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Data source + refresh
    st.markdown(
        """<div style='display:flex;align-items:center;gap:7px;
                    background:rgba(255,255,255,0.06);border-radius:8px;
                    padding:8px 10px;margin-bottom:8px'>
        <span style='font-size:14px'>📡</span>
        <div>
            <div style='font-size:11px;font-weight:600;color:rgba(255,255,255,0.85)'>
                Live SharePoint Excel</div>
            <div style='font-size:9px;color:rgba(255,255,255,0.35);margin-top:1px'>
                Auto-refreshes every 5 min</div>
        </div>
    </div>""",
        unsafe_allow_html=True,
    )

    if st.button("🔄  Refresh now", use_container_width=True):
        fetch_sharepoint.clear()
        st.rerun()

    st.markdown("---")

    # Load data
    with st.spinner("Fetching live data…"):
        try:
            file_bytes = fetch_sharepoint(SHAREPOINT_URL)
            sp_ok = True
        except Exception as sp_err:
            sp_ok = False
            sp_error = str(sp_err)

    if not sp_ok:
        st.error(f"Could not reach SharePoint: {sp_error}")
        st.stop()

    df = load_data(file_bytes)

    # ── FILTERS ────────────────────────────────────────────────────────────────
    st.markdown(
        "<div style='font-size:11px;font-weight:700;color:rgba(255,255,255,0.6);"
        "letter-spacing:0.8px;text-transform:uppercase;margin-bottom:10px'>"
        "🔍 Filters</div>",
        unsafe_allow_html=True,
    )

    # ── Quick facility search ──────────────────────────────────────────────────
    all_facs = sorted(df["Facility"].unique())
    all_districts = sorted(df["District"].unique())

    fac_search = st.text_input(
        "Search facility",
        placeholder="Type facility name…",
        label_visibility="collapsed",
    )

    # ── District quick-select ──────────────────────────────────────────────────
    st.markdown(
        "<div style='font-size:10px;font-weight:600;color:rgba(255,255,255,0.45);"
        "letter-spacing:0.5px;margin:10px 0 6px'>DISTRICT</div>",
        unsafe_allow_html=True,
    )

    sel_districts = st.multiselect(
        "Districts",
        all_districts,
        default=all_districts,
        label_visibility="collapsed",
    )

    # Quick All / None buttons for districts
    _dcol1, _dcol2 = st.columns(2)
    if _dcol1.button("All districts", use_container_width=True):
        sel_districts = all_districts
    if _dcol2.button("Clear", use_container_width=True, key="clr_dist"):
        sel_districts = []

    # ── Facility filter (respects district + search) ───────────────────────────
    st.markdown(
        "<div style='font-size:10px;font-weight:600;color:rgba(255,255,255,0.45);"
        "letter-spacing:0.5px;margin:10px 0 6px'>FACILITY</div>",
        unsafe_allow_html=True,
    )

    fac_pool = sorted(df[df["District"].isin(sel_districts)]["Facility"].unique())

    # Apply text search filter
    if fac_search:
        fac_pool = [f for f in fac_pool if fac_search.lower() in f.lower()]

    sel_facilities = st.multiselect(
        "Facilities",
        fac_pool,
        default=fac_pool,
        label_visibility="collapsed",
    )

    # Quick All / None buttons for facilities
    _fc1, _fc2 = st.columns(2)
    if _fc1.button("All facilities", use_container_width=True):
        sel_facilities = fac_pool
    if _fc2.button("Clear", use_container_width=True, key="clr_fac"):
        sel_facilities = []

    # ── Month range ────────────────────────────────────────────────────────────
    st.markdown(
        "<div style='font-size:10px;font-weight:600;color:rgba(255,255,255,0.45);"
        "letter-spacing:0.5px;margin:10px 0 6px'>MONTH RANGE</div>",
        unsafe_allow_html=True,
    )

    _m1, _m2 = st.columns(2)
    m_start = _m1.selectbox("From", MONTHS, index=0, label_visibility="collapsed")
    m_end = _m2.selectbox(
        "To", MONTHS, index=len(MONTHS) - 1, label_visibility="collapsed"
    )

    # Active filter summary
    n_sel_fac = len(sel_facilities)
    n_sel_months = len(MONTHS[MONTHS.index(m_start) : MONTHS.index(m_end) + 1])
    st.markdown(
        f"""<div style='margin-top:14px;background:rgba(255,255,255,0.05);
        border-radius:8px;padding:10px 12px;font-size:10px;
        color:rgba(255,255,255,0.5);line-height:2'>
        ✅ <b style='color:rgba(255,255,255,0.8)'>{n_sel_fac}</b> facilities selected<br>
        📅 <b style='color:rgba(255,255,255,0.8)'>{n_sel_months}</b> months selected<br>
        🟡 Gap 1 — Paper vs EHR<br>
        🔴 Gap 2 — EHR vs SHR
    </div>""",
        unsafe_allow_html=True,
    )

if df.empty:
    st.error("No data parsed. Check the file format.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# FILTER
# ─────────────────────────────────────────────────────────────────────────────
sel_months = MONTHS[MONTHS.index(m_start) : MONTHS.index(m_end) + 1]
dff = df[
    df["District"].isin(sel_districts)
    & df["Facility"].isin(sel_facilities)
    & df["Month"].isin(sel_months)
].copy()

# ─────────────────────────────────────────────────────────────────────────────
# AGGREGATES
# ─────────────────────────────────────────────────────────────────────────────
total_paper = dff["VL Paper (BAs)"].sum()
total_ehr = dff["VL EHR (BAs)"].sum()
total_shr = dff["VL SHR (Jima)"].sum()
gap1_tot = total_paper - total_ehr
gap2_tot = total_ehr - total_shr
gap1_pct = round(gap1_tot / total_paper * 100, 1) if total_paper > 0 else 0
gap2_pct = round(gap2_tot / total_ehr * 100, 1) if total_ehr > 0 else 0
n_fac = dff["Facility"].nunique()
capture_rate = round((total_ehr / total_paper) * 100, 1) if total_paper > 0 else 0
submit_rate = round((total_shr / total_ehr) * 100, 1) if total_ehr > 0 else 0
# ─────────────────────────────────────────────────────────────────────────────
# Load MoHCC logo as base64 so it works offline inside components.html
# ─────────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────────
# TOP SECTION — Animated Pipeline Dashboard (PowerPoint Style)
# ─────────────────────────────────────────────────────────────────────────────
components.html(
    f"""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }}
body {{ background: transparent; padding: 5px; }}

/* ── Container ── */
.dashboard-wrapper {{
    background: #FFFFFF;
    border: 1px solid #E8EDF3;
    border-radius: 12px;
    padding: 24px 24px 32px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}}

/* ── Header ── */
.header {{
    display: flex; justify-content: space-between; align-items: flex-start;
    margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #F1F5F9;
}}
.h-left {{ display: flex; align-items: center; gap: 16px; }}
.h-icon {{
    width: 48px; height: 48px; border-radius: 12px; background: #1E293B;
    display: flex; align-items: center; justify-content: center; font-size: 24px; color: white;
}}
.h-title {{ font-size: 18px; font-weight: 800; color: #0F172A; }}
.h-sub {{ font-size: 12px; color: #64748B; margin-top: 4px; font-weight: 500; }}
.h-tags {{ display: flex; gap: 8px; margin-top: 10px; }}
.tag {{
    background: #F1F5F9; color: #475569; padding: 4px 12px;
    border-radius: 12px; font-size: 11px; font-weight: 600;
    display: flex; align-items: center; gap: 6px;
}}
.live-dot {{ color: #10B981; font-size: 10px; }}
.h-right {{ text-align: right; position: relative; }}
.last-updated-lbl {{ font-size: 10px; color: #94A3B8; font-weight: 700; letter-spacing: 0.6px; text-transform: uppercase; }}
.last-updated-val {{ font-size: 13px; font-weight: 700; color: #0F172A; margin-top: 4px; }}

.replay-btn {{
    position: absolute; right: 0; top: 40px;
    background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px;
    padding: 6px 14px; font-size: 11px; font-weight: 700; color: #475569;
    cursor: pointer; transition: all 0.2s;
}}
.replay-btn:hover {{ background: #F1F5F9; color: #0F172A; }}

/* ── Pipeline Area ── */
.pipeline-area {{
    position: relative; width: 100%; max-width: 1000px; height: 350px; margin: 0 auto;
}}

/* ── Animations ── */
.anim-slide-right {{ opacity: 0; transform: translateX(-40px); transition: all 0.7s cubic-bezier(0.34, 1.56, 0.64, 1); }}
.anim-drop-down {{ opacity: 0; transform: translateY(-30px); transition: all 0.7s cubic-bezier(0.34, 1.56, 0.64, 1); }}
.anim-fade-up {{ opacity: 0; transform: translateY(20px); transition: all 0.6s ease-out; }}
.anim-pop {{ opacity: 0; transform: scale(0.6); transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1); }}
.visible {{ opacity: 1 !important; transform: none !important; }}

/* ── Typography (Much Larger) ── */
.text-block {{ position: absolute; text-align: center; display: flex; flex-direction: column; align-items: center; }}
.node-val {{ font-size: 32px; font-weight: 800; line-height: 1.1; }}
.val-teal {{ color: #125442; }}
.val-blue {{ color: #223B75; }}
.node-lbl {{ font-size: 14px; font-weight: 800; color: #0F172A; margin-top: 6px; text-transform: uppercase; letter-spacing: 0.3px; }}
.node-sub {{ font-size: 12px; font-weight: 500; color: #64748B; margin-top: 2px; }}

.gap-pill {{ padding: 6px 14px; border-radius: 14px; font-size: 12px; font-weight: 700; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
.pill-orange {{ background: #FFF5EC; color: #D17C32; border: 1px solid #FDE5CD; }}
.pill-red {{ background: #FEF0ED; color: #B94B39; border: 1px solid #FBD9D2; }}
.pill-blue {{ background: #EBF1FB; color: #2E5FA3; border: 1px solid #B3C8EC; }}
.gap-val {{ font-size: 26px; font-weight: 800; color: #0F172A; line-height: 1.1; margin-top: 2px; }}

.drop-val {{ font-size: 22px; font-weight: 800; position: absolute; }}
.drop-orange {{ color: #DC9F5D; }}
.drop-red {{ color: #CA6C5B; }}
.drop-blue {{ color: #2E5FA3; font-size: 22px; font-weight: 800; position: absolute; }}

/* ── Icons ── */
.icon-box {{
    width: 44px; height: 44px; background: white; border-radius: 12px;
    display: flex; align-items: center; justify-content: center; font-size: 22px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 1px solid #F1F5F9;
    position: absolute; z-index: 2;
}}

/* ── Bottom KPI Cards ── */
.kpi-row {{ display: flex; gap: 15px; margin-top: 20px; }}
.kpi-card {{
    flex: 1; background: white; border: 1px solid #E2E8F0; border-radius: 12px;
    padding: 16px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}}
.kc-top {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }}
.kc-val {{ font-size: 22px; font-weight: 800; color: #0F172A; }}
.kc-pill {{ font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 12px; }}
.kc-lbl {{ font-size: 10px; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: 0.3px; }}
.kc-sub {{ font-size: 10px; color: #64748B; margin-top: 2px; }}

</style>

<div class="dashboard-wrapper">
    <div class="header">
        <div class="h-left">
            <div class="h-icon" style="background:white;padding:3px;border:1px solid #E2E8F0;">
                    <img src="{_logo_src}"
                         style="width:100%;height:100%;object-fit:contain;border-radius:8px;"
                         alt="MoHCC Logo"/>
                </div>
            <div>
                <div class="h-title">EHR-LIMS · Viral Load Validation</div>
                <div class="h-sub">Data capture & leakage analysis across activated facilities</div>
                <div class="h-tags">
                    <span class="tag"><span class="live-dot">●</span> Live - SharePoint</span>
                    <span class="tag">{dff['District'].nunique()} districts</span>
                    <span class="tag">{n_fac} facilities</span>
                    <span class="tag">{len(sel_months)} months</span>
                </div>
            </div>
        </div>
        <div class="h-right">
            <div class="last-updated-lbl">Last updated</div>
            <div class="last-updated-val">{datetime.now().strftime('%d %b %Y - %H:%M')}</div>
            <button class="replay-btn" onclick="startAnimation()">↺ Replay</button>
        </div>
    </div>

    <div class="pipeline-area">

        <!-- ══ 3 ARROWS — text inside SVG ══ -->
        <svg width="100%" height="100%" viewBox="0 0 1000 310"
             preserveAspectRatio="xMidYMid meet"
             style="position:absolute;top:0;left:0;z-index:1;">

            <!-- ── Arrow 1: PAPER (forest green) ── -->
            <g class="anim-item anim-slide-right step-1">
                <path d="M 8,132 L 294,132 L 328,168 L 294,204 L 8,204 L 42,168 Z" fill="#1F7A4A"/>
                <text x="168" y="156" text-anchor="middle" fill="white"
                      font-size="10.5" font-weight="800" font-family="Inter,sans-serif"
                      letter-spacing="0.3">TOTAL VL SAMPLES</text>
                <text x="168" y="171" text-anchor="middle" fill="white"
                      font-size="10.5" font-weight="800" font-family="Inter,sans-serif"
                      letter-spacing="0.3">COLLECTED AT FACILITY</text>
            </g>

            <!-- ── Gap 1 branch (amber) ── -->
            <path class="anim-item anim-drop-down step-2"
                  d="M 200,204 C 248,204 290,262 330,262 L 330,253 L 362,270 L 330,287 L 330,278 C 270,278 228,204 178,204 Z"
                  fill="#D4841A"/>

            <!-- ── Arrow 2: EHR (sky teal) ── -->
            <g class="anim-item anim-slide-right step-3">
                <path d="M 358,132 L 644,132 L 678,168 L 644,204 L 358,204 L 392,168 Z" fill="#0891B2"/>
                <text x="518" y="163" text-anchor="middle" fill="white"
                      font-size="11" font-weight="800" font-family="Inter,sans-serif"
                      letter-spacing="0.4">CAPTURED IN EHR</text>
                <text x="518" y="179" text-anchor="middle" fill="rgba(255,255,255,0.8)"
                      font-size="9" font-family="Inter,sans-serif">Orders captured</text>
            </g>

            <!-- ── Gap 2 branch (slate blue) ── -->
            <path class="anim-item anim-drop-down step-4"
                  d="M 558,204 C 606,204 648,262 688,262 L 688,253 L 720,270 L 688,287 L 688,278 C 628,278 586,204 538,204 Z"
                  fill="#2E5FA3"/>

            <!-- ── Arrow 3: SHR SUBMISSION (slate blue, flat right end) ── -->
            <g class="anim-item anim-slide-right step-4">
                <path d="M 706,132 L 992,132 L 992,204 L 706,204 L 740,168 Z" fill="#2E5FA3"/>
                <text x="849" y="163" text-anchor="middle" fill="white"
                      font-size="11" font-weight="800" font-family="Inter,sans-serif"
                      letter-spacing="0.4">SHR SUBMISSION</text>
                <text x="849" y="179" text-anchor="middle" fill="rgba(255,255,255,0.8)"
                      font-size="9" font-family="Inter,sans-serif">EHR → SHR pipeline</text>
            </g>

        </svg>

        <!-- ── 12,675 above Paper ── -->
        <div class="text-block anim-item anim-fade-up step-1"
             style="left:8px;width:320px;top:26px;text-align:center;">
            <div class="node-val val-teal" id="v-paper">0</div>
        </div>

        <!-- ── Gap 1 tip: number + space + label + pill ── -->
        <div class="anim-item anim-drop-down step-2"
             style="position:absolute;left:362px;top:258px;text-align:left;">
            <div style="font-size:24px;font-weight:800;color:#D4841A;line-height:1.1;"
                 id="v-gap1-drop">0</div>
            <div id="gap1-sub"
                 style="opacity:0;transform:translateY(6px);
                        transition:opacity 0.5s ease,transform 0.5s ease;
                        margin-top:6px;">
                <div style="font-size:11px;font-weight:700;color:#A0610C;white-space:nowrap;">
                    Not recorded in EHR
                </div>
                <div class="gap-pill pill-orange" style="margin-top:6px;display:inline-block;">
                    GAP 1 · {gap1_pct}% Loss
                </div>
            </div>
        </div>

        <!-- ── 11,730 above EHR ── -->
        <div class="text-block anim-item anim-fade-up step-3"
             style="left:358px;width:286px;top:26px;text-align:center;">
            <div class="node-val" style="font-size:32px;font-weight:800;color:#0369A1;" id="v-ehr">0</div>
        </div>

        <!-- ── Gap 2 tip: number + space + label + pill ── -->
        <div class="anim-item anim-drop-down step-4"
             style="position:absolute;left:724px;top:258px;text-align:left;">
            <div style="font-size:24px;font-weight:800;color:#2E5FA3;line-height:1.1;"
                 id="v-gap2-drop">0</div>
            <div id="gap2-sub"
                 style="opacity:0;transform:translateY(6px);
                        transition:opacity 0.5s ease,transform 0.5s ease;
                        margin-top:6px;">
                <div style="font-size:11px;font-weight:700;color:#2E5FA3;white-space:nowrap;">
                    Not submitted to SHR
                </div>
                <div class="gap-pill pill-blue" style="margin-top:6px;display:inline-block;">
                    GAP 2 · {gap2_pct}% Loss
                </div>
            </div>
        </div>

        <!-- ── 6,519 above SHR ── -->
        <div class="text-block anim-item anim-fade-up step-5"
             style="left:706px;width:286px;top:26px;text-align:center;">
            <div class="node-val val-blue" id="v-shr">0</div>
        </div>

    </div>

    <div class="kpi-row anim-item anim-fade-up step-6">
        <div class="kpi-card">
            <div class="kc-top"><div class="kc-val">{int(total_paper):,}</div></div>
            <div class="kc-lbl">TOTAL PAPER SAMPLES</div>
            <div class="kc-sub">VL samples collected at {n_fac} sites</div>
        </div>
        <div class="kpi-card">
            <div class="kc-top">
                <div class="kc-val">{int(total_ehr):,}</div>
                <div class="kc-pill" style="background: #ECFDF5; color: #059669;">{capture_rate}%</div>
            </div>
            <div class="kc-lbl">CAPTURED IN EHR</div>
            <div class="kc-sub">Capture Rate</div>
        </div>
        <div class="kpi-card">
            <div class="kc-top">
                <div class="kc-val">{int(total_shr):,}</div>
                <div class="kc-pill" style="background: #EFF6FF; color: #2563EB;">{submit_rate}%</div>
            </div>
            <div class="kc-lbl">SUBMITTED TO SHR</div>
            <div class="kc-sub">Submission Rate</div>
        </div>
        <div class="kpi-card">
            <div class="kc-top">
                <div class="kc-val">{int(gap1_tot):,}</div>
                <div class="kc-pill" style="background: #FFF7ED; color: #D17C32;">{gap1_pct}% Loss</div>
            </div>
            <div class="kc-lbl">GAP 1 – PAPER VS EHR</div>
            <div class="kc-sub">Not recorded in EHR</div>
        </div>
        <div class="kpi-card">
            <div class="kc-top">
                <div class="kc-val">{int(gap2_tot):,}</div>
                <div class="kc-pill" style="background: #FEF2F2; color: #B94B39;">{gap2_pct}% Loss</div>
            </div>
            <div class="kc-lbl">GAP 2 – EHR VS SHR</div>
            <div class="kc-sub">Not submitted to SHR</div>
        </div>
    </div>
</div>

<script>
var VALS = {{
  paper: {int(total_paper)},
  ehr:   {int(total_ehr)},
  shr:   {int(total_shr)},
  gap1:  {int(gap1_tot)},
  gap2:  {int(gap2_tot)}
}};

function countUp(id, target, dur, delay) {{
  setTimeout(function() {{
    var el = document.getElementById(id);
    if (!el) return;
    var t0 = performance.now();
    (function tick(now) {{
      var p = Math.min((now - t0) / dur, 1), e = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.floor(e * target).toLocaleString();
      if (p < 1) requestAnimationFrame(tick);
      else el.textContent = target.toLocaleString();
    }})(performance.now());
  }}, delay);
}}

function revealSub(id, delay) {{
  setTimeout(function() {{
    var el = document.getElementById(id);
    if (el) {{ el.style.opacity = '1'; el.style.transform = 'translateY(0)'; }}
  }}, delay);
}}

function startAnimation() {{
  document.querySelectorAll('.anim-item').forEach(el => el.classList.remove('visible'));
  ['gap1-sub','gap2-sub'].forEach(function(id) {{
    var el = document.getElementById(id);
    if (el) {{ el.style.opacity = '0'; el.style.transform = 'translateY(8px)'; }}
  }});
  ['v-paper','v-ehr','v-shr','v-gap1-drop','v-gap2-drop'].forEach(function(id) {{
    var el = document.getElementById(id); if (el) el.textContent = '0';
  }});

  const timeline = [
    {{ step: 1, delay: 200  }},
    {{ step: 2, delay: 1300 }},
    {{ step: 3, delay: 2400 }},
    {{ step: 4, delay: 3500 }},
    {{ step: 5, delay: 4600 }},
    {{ step: 6, delay: 5600 }}
  ];
  timeline.forEach(t => {{
    setTimeout(() => {{
      document.querySelectorAll('.step-' + t.step).forEach(el => el.classList.add('visible'));
    }}, t.delay);
  }});

  // Count-up all values
  countUp('v-paper',     VALS.paper, 900, 300);
  countUp('v-gap1-drop', VALS.gap1,  700, 1400);
  countUp('v-ehr',       VALS.ehr,   900, 2500);
  countUp('v-gap2-drop', VALS.gap2,  700, 3600);
  countUp('v-shr',       VALS.shr,   900, 4700);

  // Reveal sub-text AFTER number finishes
  revealSub('gap1-sub', 2150);
  revealSub('gap2-sub', 4350);
}}

window.addEventListener('DOMContentLoaded', startAnimation);
</script>
""",
    height=650,
)
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
# MONTHLY CASCADE EXPLORER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """<div style="font-size:14px;font-weight:600;color:#0D1B2A;
    margin:28px 0 14px;display:flex;align-items:center;gap:8px">
    📅 Monthly cascade explorer
    <span style="flex:1;height:1px;background:#E8EDF3;display:inline-block;margin-left:8px"></span>
</div>""",
    unsafe_allow_html=True,
)

# ── Build monthly summary ─────────────────────────────────────────────────────
MONTHS_ORDER = ["Oct-25", "Nov-25", "Dec-25", "Jan-26", "Feb-26", "Mar-26", "Apr-26"]
monthly_all = dff.groupby("Month", as_index=False).agg(
    Paper=("VL Paper (BAs)", "sum"),
    EHR=("VL EHR (BAs)", "sum"),
    SHR=("VL SHR (Jima)", "sum"),
    Facs=("Facility", "nunique"),
)
monthly_all["Month"] = pd.Categorical(
    monthly_all["Month"], categories=MONTHS_ORDER, ordered=True
)
monthly_all = monthly_all.sort_values("Month").reset_index(drop=True)
monthly_all["Gap1"] = monthly_all["Paper"] - monthly_all["EHR"]
monthly_all["Gap2"] = monthly_all["EHR"] - monthly_all["SHR"]
monthly_all["Gap1 %"] = (monthly_all["Gap1"] / monthly_all["Paper"] * 100).round(1)
monthly_all["Gap2 %"] = (monthly_all["Gap2"] / monthly_all["EHR"] * 100).round(1)
monthly_all["Capture %"] = (monthly_all["EHR"] / monthly_all["Paper"] * 100).round(1)
monthly_all["Submit %"] = (monthly_all["SHR"] / monthly_all["EHR"] * 100).round(1)

avail_months = [m for m in MONTHS_ORDER if m in monthly_all["Month"].values]

# ── Grouped bar chart — Paper / EHR / SHR by month ───────────────────────────
# Pre-compute per-month facility hover text (ordered by gap %)
_hover_paper = []  # Gap 1 breakdown on Paper bar
_hover_ehr = []  # Gap 2 breakdown on EHR bar
_hover_shr = []  # Gap 2 breakdown on SHR bar

for _m in monthly_all["Month"]:
    _mf = dff[dff["Month"] == _m].copy()
    _mf["_g1"] = _mf["VL Paper (BAs)"] - _mf["VL EHR (BAs)"]
    _mf["_g1p"] = np.where(
        _mf["VL Paper (BAs)"] > 0,
        (_mf["_g1"] / _mf["VL Paper (BAs)"] * 100).round(1),
        np.nan,
    )
    _mf["_g2"] = _mf["VL EHR (BAs)"] - _mf["VL SHR (Jima)"]
    _mf["_g2p"] = np.where(
        _mf["VL EHR (BAs)"] > 0,
        (_mf["_g2"] / _mf["VL EHR (BAs)"] * 100).round(1),
        np.nan,
    )

    # Paper bar → show Gap 1 by facility
    _s1 = _mf.sort_values("_g1p", ascending=False).dropna(subset=["_g1p"])
    _h1 = f"<b>Gap 1 — facilities ({_m})</b><br>" + "<br>".join(
        f"{'🔴' if r['_g1p']>30 else '🟡' if r['_g1p']>10 else '🟢'} "
        f"{r['Facility']}: {int(r['_g1']):,} &nbsp;({r['_g1p']}%)"
        for _, r in _s1.iterrows()
    )
    _hover_paper.append(_h1)

    # EHR bar → show Gap 2 by facility
    _s2 = _mf.sort_values("_g2p", ascending=False).dropna(subset=["_g2p"])
    _h2 = f"<b>Gap 2 — facilities ({_m})</b><br>" + "<br>".join(
        f"{'🔴' if r['_g2p']>30 else '🟡' if r['_g2p']>10 else '🟢'} "
        f"{r['Facility']}: {int(r['_g2']):,} &nbsp;({r['_g2p']}%)"
        for _, r in _s2.iterrows()
    )
    _hover_ehr.append(_h2)
    _hover_shr.append(_h2)

fig_monthly_bar = go.Figure()

# Paper bars
fig_monthly_bar.add_bar(
    x=monthly_all["Month"],
    y=monthly_all["Paper"],
    name="Total VL Collected",
    marker_color="#1F7A4A",
    text=monthly_all["Paper"].apply(lambda v: f"{int(v):,}" if not pd.isna(v) else ""),
    textposition="outside",
    textfont=dict(size=9, color="#374151"),
    customdata=_hover_paper,
    hovertemplate="%{customdata}<extra></extra>",
)

# EHR bars
fig_monthly_bar.add_bar(
    x=monthly_all["Month"],
    y=monthly_all["EHR"],
    name="Captured in EHR",
    marker_color="#0891B2",
    text=monthly_all["EHR"].apply(lambda v: f"{int(v):,}" if not pd.isna(v) else ""),
    textposition="outside",
    textfont=dict(size=9, color="#374151"),
    customdata=_hover_ehr,
    hovertemplate="%{customdata}<extra></extra>",
)

# SHR bars
fig_monthly_bar.add_bar(
    x=monthly_all["Month"],
    y=monthly_all["SHR"],
    name="Submitted to SHR",
    marker_color="#2E5FA3",
    text=monthly_all["SHR"].apply(lambda v: f"{int(v):,}" if not pd.isna(v) else ""),
    textposition="outside",
    textfont=dict(size=9, color="#374151"),
    hovertemplate="<b>%{x}</b><br>Submitted to SHR: %{y:,.0f}<extra></extra>",
)

fig_monthly_bar.update_layout(
    barmode="group",
    height=400,
    margin=dict(l=10, r=10, t=70, b=10),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.08,
        xanchor="left",
        x=0,
        font=dict(size=11),
        bgcolor="rgba(0,0,0,0)",
    ),
    xaxis=dict(gridcolor="#F1F5F9", tickfont=dict(size=11)),
    yaxis=dict(gridcolor="#F1F5F9", title="Sample count", tickfont=dict(size=10)),
    plot_bgcolor="white",
    paper_bgcolor="white",
    hovermode="closest",
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="#E2E8F0",
        font=dict(size=11, family="Inter, sans-serif"),
        align="left",
    ),
    title=dict(
        text=(
            '<b style="font-size:14px">Paper vs EHR vs SHR by month</b><br>'
            '<span style="font-size:11px;color:#94A3B8">'
            "Hover each bar to see facility breakdown ordered by gap %"
            "</span>"
        ),
        font=dict(size=14),
        x=0.01,
        y=0.97,
        yanchor="top",
        pad=dict(b=16),
    ),
)
st.plotly_chart(fig_monthly_bar, use_container_width=True)

# ── Auto-detect insights ──────────────────────────────────────────────────────
best_capture = monthly_all.loc[monthly_all["Capture %"].idxmax()]
worst_capture = monthly_all.loc[monthly_all["Capture %"].idxmin()]
best_submit = monthly_all.loc[monthly_all["Submit %"].idxmax()]
worst_submit = monthly_all.loc[monthly_all["Submit %"].idxmin()]
highest_paper = monthly_all.loc[monthly_all["Paper"].idxmax()]
lowest_paper = monthly_all.loc[monthly_all["Paper"].idxmin()]

# ── Insight banner ────────────────────────────────────────────────────────────
ic1, ic2, ic3, ic4 = st.columns(4)


def insight_card(col, icon, title, month, value, color, bg):
    col.markdown(
        f"""
    <div style="background:{bg};border-radius:10px;padding:14px 16px;
                border-left:4px solid {color};border:1px solid {color}30;">
        <div style="font-size:18px;margin-bottom:4px">{icon}</div>
        <div style="font-size:9px;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.6px;color:{color};margin-bottom:3px">{title}</div>
        <div style="font-size:15px;font-weight:800;color:#0F172A">{month}</div>
        <div style="font-size:11px;color:#64748B;margin-top:2px">{value}</div>
    </div>""",
        unsafe_allow_html=True,
    )


insight_card(
    ic1,
    "🏆",
    "Best EHR capture",
    best_capture["Month"],
    f"{best_capture['Capture %']}% capture rate · {int(best_capture['EHR']):,} orders",
    "#059669",
    "#F0FDF4",
)
insight_card(
    ic2,
    "⚠️",
    "Worst EHR capture",
    worst_capture["Month"],
    f"{worst_capture['Capture %']}% capture rate · {int(worst_capture['Gap1']):,} missed",
    "#B45309",
    "#FFFBEB",
)
insight_card(
    ic3,
    "✅",
    "Best SHR submission",
    best_submit["Month"],
    f"{best_submit['Submit %']}% submission rate · {int(best_submit['SHR']):,} sent",
    "#2563EB",
    "#EFF6FF",
)
insight_card(
    ic4,
    "🔴",
    "Worst SHR submission",
    worst_submit["Month"],
    f"{worst_submit['Submit %']}% submission rate · {int(worst_submit['Gap2']):,} missed",
    "#B91C1C",
    "#FEF2F2",
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Month slider ──────────────────────────────────────────────────────────────
sel_month = st.select_slider(
    "🗓️ Slide to explore a month",
    options=avail_months,
    value=avail_months[-1],
)

mrow = monthly_all[monthly_all["Month"] == sel_month].iloc[0]
avg_paper = monthly_all["Paper"].mean()
avg_ehr = monthly_all["EHR"].mean()
avg_shr = monthly_all["SHR"].mean()

# ── Facility breakdown — animated ranked bar charts ───────────────────────────
st.markdown(
    f"""<div style="font-size:14px;font-weight:600;color:#0D1B2A;
    margin:20px 0 12px;display:flex;align-items:center;gap:8px">
    Facility performance — {sel_month}
    <span style="flex:1;height:1px;background:#E8EDF3;display:inline-block;margin-left:8px"></span>
</div>""",
    unsafe_allow_html=True,
)

fac_month = dff[dff["Month"] == sel_month].copy()
fac_month["Gap1"] = fac_month["VL Paper (BAs)"] - fac_month["VL EHR (BAs)"]
fac_month["Gap2"] = fac_month["VL EHR (BAs)"] - fac_month["VL SHR (Jima)"]
fac_month["Gap1 %"] = (fac_month["Gap1"] / fac_month["VL Paper (BAs)"] * 100).round(1)
fac_month["Gap2 %"] = (fac_month["Gap2"] / fac_month["VL EHR (BAs)"] * 100).round(1)


def _bar_color(pct):
    if pd.isna(pct) or pct < 0:
        return "#3B82F6"
    if pct > 30:
        return "#EF4444"
    if pct > 10:
        return "#F59E0B"
    return "#10B981"


def _build_animated_chart(df, val_col, pct_col, abs_col, title, subtitle):
    """Build a Plotly figure that reveals bars one-by-one, worst first."""
    s = df.dropna(subset=[pct_col]).sort_values(pct_col, ascending=False)
    s = s.reset_index(drop=True)

    facs = s["Facility"].tolist()
    pcts = s[pct_col].tolist()
    absv = s[abs_col].tolist()
    colors = [_bar_color(p) for p in pcts]

    n = len(facs)
    # Each frame reveals one more bar (worst → best)
    frames = []
    for i in range(n + 1):
        bar_x = pcts[:i] + [0] * (n - i)
        bar_text = [f"{absv[j]:,.0f}  ({pcts[j]}%)" for j in range(i)] + [""] * (n - i)
        frames.append(
            go.Frame(
                data=[
                    go.Bar(
                        x=bar_x,
                        y=facs,
                        orientation="h",
                        marker_color=colors,
                        text=bar_text,
                        textposition="outside",
                        textfont=dict(size=10, color="#374151"),
                        width=0.6,
                    )
                ],
                name=str(i),
            )
        )

    fig = go.Figure(
        data=[
            go.Bar(
                x=[0] * n,
                y=facs,
                orientation="h",
                marker_color=colors,
                text=[""] * n,
                textposition="outside",
                width=0.6,
            )
        ],
        frames=frames,
    )
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b><br>"
            f'<span style="font-size:11px;color:#94A3B8">{subtitle}</span>',
            font=dict(size=13),
            x=0.01,
        ),
        height=max(320, n * 38 + 80),
        margin=dict(l=10, r=80, t=65, b=10),
        xaxis=dict(
            title="Gap %",
            ticksuffix="%",
            gridcolor="#F1F5F9",
            zeroline=True,
            zerolinecolor="#CBD5E1",
            zerolinewidth=1.5,
            range=[-5, max(max(pcts) + 10, 10)],
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=11),
            tickmode="array",
            tickvals=facs,
            ticktext=facs,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                visible=False,  # hidden — JS clicks it automatically
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            dict(
                                frame=dict(duration=120, redraw=True),
                                fromcurrent=True,
                                mode="immediate",
                                transition=dict(duration=80, easing="cubic-in-out"),
                            ),
                        ],
                    )
                ],
            )
        ],
    )
    return fig


_g1_chart = _build_animated_chart(
    fac_month,
    "VL EHR (BAs)",
    "Gap1 %",
    "Gap1",
    "Gap 1 — Paper vs EHR (samples not entered into EHR)",
    f"Worst → best · {sel_month} · 🔴 >30%  🟡 10–30%  🟢 <10%",
)
_g2_chart = _build_animated_chart(
    fac_month,
    "VL SHR (Jima)",
    "Gap2 %",
    "Gap2",
    "Gap 2 — EHR vs SHR (orders not submitted to SHR)",
    f"Worst → best · {sel_month} · 🔴 >30%  🟡 10–30%  🟢 <10%",
)

import plotly.io as _pio


def _animated_chart_html(fig, chart_id):
    """Convert Plotly figure to self-contained HTML that auto-plays."""
    html = _pio.to_html(
        fig,
        include_plotlyjs="cdn",
        div_id=chart_id,
        full_html=False,
        config=dict(displayModeBar=False),
    )
    autoplay = f"""
<script>
(function() {{
    function tryPlay() {{
        var el = document.getElementById('{chart_id}');
        if (!el) {{ setTimeout(tryPlay, 200); return; }}
        setTimeout(function() {{
            Plotly.animate('{chart_id}', null, {{
                frame: {{duration: 120, redraw: true}},
                transition: {{duration: 80, easing: 'cubic-in-out'}},
                mode: 'immediate'
            }});
        }}, 400);
    }}
    if (typeof Plotly !== 'undefined') {{ tryPlay(); }}
    else {{ window.addEventListener('load', tryPlay); }}
}})();
</script>"""
    return html + autoplay


_ch1, _ch2 = st.columns(2)
with _ch1:
    import streamlit.components.v1 as _comp

    _comp.html(
        _animated_chart_html(_g1_chart, f'gap1_{sel_month.replace("-","")}'),
        height=_g1_chart.layout.height + 40,
    )
with _ch2:
    _comp.html(
        _animated_chart_html(_g2_chart, f'gap2_{sel_month.replace("-","")}'),
        height=_g2_chart.layout.height + 40,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GAP CHARTS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="font-size:14px;font-weight:600;color:#0D1B2A;margin:28px 0 12px;display:flex;align-items:center;gap:8px">📊 Data leakage by facility<span style="flex:1;height:1px;background:#E8EDF3;display:inline-block;margin-left:8px"></span></div>',
    unsafe_allow_html=True,
)

col_a, col_b = st.columns(2)


def styled_bar(
    df_in, bg_col, fg_col, bg_name, fg_name, gap_col, gap_pct_col, title, subtitle
):
    s = df_in.sort_values(gap_col, ascending=False)
    colors = []
    for v in s[gap_pct_col]:
        if pd.isna(v):
            colors.append("#94A3B8")
        elif v > 30:
            colors.append("#EF4444")
        elif v > 10:
            colors.append("#F59E0B")
        else:
            colors.append("#10B981")

    fig = go.Figure()
    fig.add_bar(
        y=s["Facility"],
        x=s[bg_col],
        name=bg_name,
        orientation="h",
        marker_color="#E2E8F0",
        hovertemplate="<b>%{y}</b><br>" + bg_name + ": %{x:,}<extra></extra>",
    )
    fig.add_bar(
        y=s["Facility"],
        x=s[fg_col],
        name=fg_name,
        orientation="h",
        marker_color=colors,
        hovertemplate="<b>%{y}</b><br>"
        + fg_name
        + ": %{x:,}<br>Gap: %{customdata:.1f}%<extra></extra>",
        customdata=s[gap_pct_col],
    )
    fig.update_layout(
        title=dict(
            text=f'<b>{title}</b><br><span style="font-size:11px;color:#94A3B8">{subtitle}</span>',
            font=dict(size=13),
            x=0,
        ),
        barmode="overlay",
        height=420,
        margin=dict(l=10, r=20, t=60, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.08, font=dict(size=11)),
        xaxis=dict(title="Sample count", gridcolor="#F1F5F9", tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10)),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig


with col_a:
    st.plotly_chart(
        styled_bar(
            fac,
            "Paper",
            "EHR",
            "Total VL Collected",
            "EHR Captured",
            "Gap1",
            "Gap1 %",
            "Gap 1 — Paper vs EHR",
            "Colour = severity: red >30% · amber 10–30% · green <10%",
        ),
        use_container_width=True,
    )

with col_b:
    st.plotly_chart(
        styled_bar(
            fac,
            "EHR",
            "SHR",
            "EHR (BAs)",
            "SHR Submitted",
            "Gap2",
            "Gap2 %",
            "Gap 2 — EHR vs SHR",
            "Colour = severity: red >30% · amber 10–30% · green <10%",
        ),
        use_container_width=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# MONTHLY TREND + CAPTURE RATE DONUT
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="font-size:14px;font-weight:600;color:#0D1B2A;margin:28px 0 12px;display:flex;align-items:center;gap:8px">📈 Monthly trend & capture rates<span style="flex:1;height:1px;background:#E8EDF3;display:inline-block;margin-left:8px"></span></div>',
    unsafe_allow_html=True,
)

col_trend, col_donut = st.columns([2.2, 1])

monthly = dff.groupby("Month", as_index=False).agg(
    Paper=("VL Paper (BAs)", "sum"),
    EHR=("VL EHR (BAs)", "sum"),
    SHR=("VL SHR (Jima)", "sum"),
)
monthly["Month Date"] = monthly["Month"].map(MONTH_DATES)
monthly = monthly.sort_values("Month Date")
monthly["Gap1"] = monthly["Paper"] - monthly["EHR"]
monthly["Gap2"] = monthly["EHR"] - monthly["SHR"]

with col_trend:
    fig_trend = go.Figure()
    # Fill area between Paper and EHR (gap 1)
    fig_trend.add_scatter(
        x=monthly["Month"],
        y=monthly["Paper"],
        name="Total VL Collected",
        mode="lines+markers",
        line=dict(color="#3B82F6", width=2.5),
        marker=dict(size=8, color="white", line=dict(color="#3B82F6", width=2)),
        fill=None,
    )
    fig_trend.add_scatter(
        x=monthly["Month"],
        y=monthly["EHR"],
        name="EHR (BAs)",
        mode="lines+markers",
        line=dict(color="#10B981", width=2.5),
        marker=dict(size=8, color="white", line=dict(color="#10B981", width=2)),
        fill="tonexty",
        fillcolor="rgba(59,130,246,0.07)",
    )
    fig_trend.add_scatter(
        x=monthly["Month"],
        y=monthly["SHR"],
        name="SHR (Jima)",
        mode="lines+markers",
        line=dict(color="#8B5CF6", width=2.5),
        marker=dict(size=8, color="white", line=dict(color="#8B5CF6", width=2)),
        fill="tonexty",
        fillcolor="rgba(16,185,129,0.07)",
    )
    fig_trend.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
        xaxis=dict(gridcolor="#F1F5F9"),
        yaxis=dict(gridcolor="#F1F5F9", title="Samples"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="x unified",
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col_donut:
    # Funnel/donut showing overall pipeline retention
    fig_donut = go.Figure(
        go.Funnel(
            y=["Paper collected", "Captured in EHR", "Submitted to SHR"],
            x=[int(total_paper), int(total_ehr), int(total_shr)],
            textinfo="value+percent initial",
            marker=dict(
                color=["#3B82F6", "#10B981", "#8B5CF6"],
                line=dict(color="white", width=2),
            ),
            connector=dict(line=dict(color="#F1F5F9", width=1)),
            textfont=dict(size=11),
        )
    )
    fig_donut.update_layout(
        title=dict(text="<b>Pipeline retention</b>", font=dict(size=13), x=0.02),
        height=300,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# LEADERBOARD + DRILLDOWN
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="sec-hdr">🏆 Leakage leaderboard & facility drilldown</div>',
    unsafe_allow_html=True,
)

col_lb, col_drill = st.columns([1.3, 1])

with col_lb:
    board = fac.sort_values("Gap1 %", ascending=False).reset_index(drop=True)

    def badge(pct):
        if pd.isna(pct):
            return f'<span class="lb-badge badge-purple">N/A</span>'
        if pct > 30:
            return f'<span class="lb-badge badge-red">{pct:.1f}%</span>'
        if pct > 10:
            return f'<span class="lb-badge badge-amber">{pct:.1f}%</span>'
        return f'<span class="lb-badge badge-green">{pct:.1f}%</span>'

    def mini_bar(ehr, paper, color):
        pct = min(ehr / paper * 100, 100) if paper > 0 else 0
        return f"""<div style="background:#F1F5F9;border-radius:4px;height:6px;width:100%">
            <div style="background:{color};height:6px;border-radius:4px;width:{pct:.0f}%"></div>
        </div>"""

    html_rows = ""
    for i, row in board.iterrows():
        critical = (
            " critical" if (not pd.isna(row["Gap1 %"]) and row["Gap1 %"] > 30) else ""
        )
        rank_icon = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
        html_rows += f"""
        <div class="lb-row{critical}">
          <div class="lb-rank">{rank_icon}</div>
          <div class="lb-name">
            <div class="lbn-fac">{row['Facility']}</div>
            <div class="lbn-dist">{row['District']}</div>
          </div>
          <div class="lb-bars" style="font-size:11px;color:#64748B">
            Gap 1: {badge(row['Gap1 %'])} &nbsp; Gap 2: {badge(row['Gap2 %'])}
            <div style="margin-top:5px">{mini_bar(row['EHR'], row['Paper'], '#10B981')}</div>
            <div style="font-size:9px;color:#CBD5E1;margin-top:2px">EHR capture rate</div>
          </div>
        </div>"""

    components.html(
        f"""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    * {{ font-family: 'Inter', sans-serif; box-sizing: border-box; }}
    .lb-row {{ display:flex;align-items:center;padding:10px 14px;border-radius:10px;
               margin-bottom:6px;gap:12px;background:#FAFBFC;
               border:1px solid #F1F5F9;transition:background 0.15s; }}
    .lb-row:hover {{ background:#F1F5F9; }}
    .lb-rank {{ font-size:13px;font-weight:700;color:#94A3B8;min-width:28px; }}
    .lb-name {{ flex:1; }}
    .lbn-fac {{ font-size:13px;font-weight:600;color:#0D1B2A; }}
    .lbn-dist {{ font-size:11px;color:#94A3B8; }}
    .lb-bars {{ flex:0 0 190px; }}
    .lb-badge {{ font-size:11px;font-weight:700;border-radius:20px;padding:2px 9px;white-space:nowrap; }}
    .badge-red    {{ background:#FFF1F2;color:#BE123C;border:1px solid #FECDD3; }}
    .badge-amber  {{ background:#FFFBEB;color:#B45309;border:1px solid #FDE68A; }}
    .badge-green  {{ background:#F0FDF4;color:#15803D;border:1px solid #BBF7D0; }}
    .badge-purple {{ background:#F5F3FF;color:#6D28D9;border:1px solid #DDD6FE; }}
    @keyframes pulse-red {{
      0%,100% {{ box-shadow:0 0 0 0 rgba(239,68,68,0); }}
      50%      {{ box-shadow:0 0 0 6px rgba(239,68,68,0.15); }}
    }}
    .critical {{ animation:pulse-red 2.5s ease-in-out infinite;
                 border-color:#FECDD3!important;background:#FFF5F5!important; }}
    </style>
    <div>{html_rows}</div>
    """,
        height=min(80 * len(board) + 20, 520),
        scrolling=True,
    )

with col_drill:
    sel_fac = st.selectbox(
        "Select facility",
        sorted(dff["Facility"].unique()),
        label_visibility="collapsed",
    )
    fac_df = dff[dff["Facility"] == sel_fac].sort_values("Month Date")
    act = fac_df["Activation Date"].iloc[0] if not fac_df.empty else None
    dist = fac_df["District"].iloc[0] if not fac_df.empty else "—"
    g1 = fac_df["Gap1"].sum()
    g2 = fac_df["Gap2"].sum()
    g1p = fac_df["Gap1 %"].mean()
    g2p = fac_df["Gap2 %"].mean()

    # Mini stat row
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown(
            f"""<div class="drill-stat">
            <div class="ds-lbl">District</div>
            <div class="ds-val" style="font-size:15px">{dist}</div>
        </div>
        <div class="drill-stat">
            <div class="ds-lbl">Gap 1 total</div>
            <div class="ds-val" style="color:#F59E0B">{int(g1):,} <span style="font-size:12px">({g1p:.1f}%)</span></div>
        </div>""",
            unsafe_allow_html=True,
        )
    with sc2:
        st.markdown(
            f"""<div class="drill-stat">
            <div class="ds-lbl">Activated</div>
            <div class="ds-val" style="font-size:15px">{act.strftime('%b %Y') if act else '—'}</div>
        </div>
        <div class="drill-stat">
            <div class="ds-lbl">Gap 2 total</div>
            <div class="ds-val" style="color:#EF4444">{int(g2):,} <span style="font-size:12px">({g2p:.1f}%)</span></div>
        </div>""",
            unsafe_allow_html=True,
        )

    fig_drill = go.Figure()
    fig_drill.add_scatter(
        x=fac_df["Month"],
        y=fac_df["VL Paper (BAs)"],
        name="Paper",
        mode="lines+markers",
        line=dict(color="#3B82F6", width=2.5),
        marker=dict(size=9, color="white", line=dict(color="#3B82F6", width=2)),
    )
    fig_drill.add_scatter(
        x=fac_df["Month"],
        y=fac_df["VL EHR (BAs)"],
        name="EHR",
        mode="lines+markers",
        line=dict(color="#10B981", width=2.5),
        marker=dict(size=9, color="white", line=dict(color="#10B981", width=2)),
    )
    fig_drill.add_scatter(
        x=fac_df["Month"],
        y=fac_df["VL SHR (Jima)"],
        name="SHR",
        mode="lines+markers",
        line=dict(color="#8B5CF6", width=2.5),
        marker=dict(size=9, color="white", line=dict(color="#8B5CF6", width=2)),
    )
    fig_drill.update_layout(
        height=220,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)),
        xaxis=dict(gridcolor="#F1F5F9", tickfont=dict(size=9)),
        yaxis=dict(gridcolor="#F1F5F9", tickfont=dict(size=9)),
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="x unified",
    )
    st.plotly_chart(fig_drill, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """<div style="text-align:center;margin-top:32px;padding:16px;
    color:#94A3B8;font-size:11px;border-top:1px solid #E8EDF3;">
    🔴 >30% gap · 🟡 10–30% · 🟢 &lt;10% &nbsp;|&nbsp;
    Analysis starts the month <i>after</i> facility go-live &nbsp;|&nbsp;
    Zim-TTECH · EHR–LIMS Validation
</div>""",
    unsafe_allow_html=True,
)
