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
    layout="wide", page_icon="🔬",
    initial_sidebar_state="expanded"
)


# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
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
    border: 1px solid #DBEAFE; position: relative; overflow: hidden;
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
.kpi-card .kc-sub  { font-size: 11px; color: #64748B; margin-top: 4px; }
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
    border: 1px solid #DBEAFE; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* ── leaderboard ── */
.lb-row {
    display: flex; align-items: center; padding: 10px 14px;
    border-radius: 10px; margin-bottom: 6px; gap: 12px;
    background: #FAFBFC; border: 1px solid #F1F5F9; transition: background 0.15s;
}
.lb-row:hover { background: #F1F5F9; }
.lb-rank { font-size: 13px; font-weight: 700; color: #64748B; min-width: 22px; }
.lb-name { flex: 1; }
.lb-name .lbn-fac { font-size: 13px; font-weight: 600; color: #0D1B2A; }
.lb-name .lbn-dist { font-size: 11px; color: #64748B; }
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
    background: #F8FAFF !important;
    border-right: 1px solid #DBEAFE !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}

/* Text — scoped tightly to avoid hiding the sidebar collapse toggle in Chrome */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span:not([data-baseweb="tag"] span),
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stCheckbox label { color: #1E3A5F; }

/* Inputs */
[data-testid="stSidebar"] input {
    background: white !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 7px !important;
    color: #0F172A !important;
    font-size: 12px !important;
}
[data-testid="stSidebar"] input::placeholder { color: #94A3B8 !important; }

/* Multiselect / selectbox */
[data-testid="stSidebar"] .stMultiSelect > div > div,
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: white !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 7px !important;
    font-size: 12px !important;
}

/* Selected pills */
[data-testid="stSidebar"] span[data-baseweb="tag"] {
    background: #EFF6FF !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 5px !important;
    padding: 1px 7px !important;
}
[data-testid="stSidebar"] span[data-baseweb="tag"] span {
    color: #1D4ED8 !important;
    font-size: 11px !important;
    font-weight: 500 !important;
}

/* Buttons */
[data-testid="stSidebar"] button {
    background: #1E3A5F !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    transition: background 0.15s !important;
}
[data-testid="stSidebar"] button:hover { background: #0F2744 !important; }
[data-testid="stSidebar"] button p,
[data-testid="stSidebar"] button span { color: white !important; }

/* Divider */
[data-testid="stSidebar"] hr { border-color: #E2E8F0 !important; margin: 10px 0 !important; }

/* Scrollbar */
[data-testid="stSidebar"]::-webkit-scrollbar { width: 3px; }
[data-testid="stSidebar"]::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 4px; }

/* ── drilldown ── */
.drill-stat { background: #F0F7FF; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; border: 1px solid #DBEAFE; }
.drill-stat .ds-lbl { font-size: 11px; color: #64748B; font-weight: 500; }
.drill-stat .ds-val { font-size: 18px; font-weight: 700; color: #0D1B2A; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
MONTHS = ['Oct-25','Nov-25','Dec-25','Jan-26','Feb-26','Mar-26','Apr-26']
MONTH_DATES = {
    'Oct-25': datetime(2025,10,1), 'Nov-25': datetime(2025,11,1),
    'Dec-25': datetime(2025,12,1), 'Jan-26': datetime(2026,1,1),
    'Feb-26': datetime(2026,2,1),  'Mar-26': datetime(2026,3,1),
    'Apr-26': datetime(2026,4,1),
}

PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        font=dict(family='Inter, sans-serif', color='#334155'),
        plot_bgcolor='white', paper_bgcolor='white',
        colorway=['#3B82F6','#10B981','#8B5CF6','#F59E0B','#EF4444','#06B6D4'],
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
            "application/vnd.openxmlformats-officedocument"
            ".spreadsheetml.sheet,*/*"
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
    if pd.isna(v): return np.nan
    s = str(v).strip()
    if s in ['N/A','','#VALUE!','nan','-']: return np.nan
    try:    return float(s)
    except: return np.nan

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
        if district in ['','nan'] or facility in ['','nan']:
            continue
        activation_date = None
        try:
            activation_date = pd.to_datetime(str(row[2]).strip(), dayfirst=True)
        except Exception:
            pass
        act_month = datetime(activation_date.year, activation_date.month, 1) if activation_date else None

        for j, month in enumerate(MONTHS):
            if act_month and MONTH_DATES[month] <= act_month:
                continue
            records.append({
                'District':        district,
                'Facility':        facility,
                'Activation Date': activation_date,
                'Month':           month,
                'Month Date':      MONTH_DATES[month],
                'VL Paper (BAs)':  parse_val(row[3  + j]),
                'VL LIMS':         parse_val(row[10 + j]),
                'VL EHR (BAs)':    parse_val(row[17 + j]),
                'VL SHR (Jima)':   parse_val(row[24 + j]),
            })

    df = pd.DataFrame(records)
    if df.empty: return df
    df['Gap1'] = df['VL Paper (BAs)'] - df['VL EHR (BAs)']
    df['Gap2'] = df['VL EHR (BAs)']   - df['VL SHR (Jima)']
    df['Gap1 %'] = np.where(df['VL Paper (BAs)'] > 0,
                    (df['Gap1']/df['VL Paper (BAs)']*100).round(1), np.nan)
    df['Gap2 %'] = np.where(df['VL EHR (BAs)'] > 0,
                    (df['Gap2']/df['VL EHR (BAs)']*100).round(1), np.nan)
    return df

# Load MoHCC logo as base64 so it works offline inside components.html
# ─────────────────────────────────────────────────────────────────────────────
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

    # ── Header ────────────────────────────────────────────────────────────────
    _logo_img = f"<img src='{_logo_src}' style='width:32px;height:32px;object-fit:contain;border-radius:6px;background:#E8F0FE;padding:2px;flex-shrink:0;' alt=''/>" if _logo_src else "<span style='font-size:22px'>🔬</span>"
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#0F2744,#1B4070);
                border-radius:12px;padding:16px;margin-bottom:16px'>
      <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px'>
        {_logo_img}
        <div>
          <div style='font-size:14px;font-weight:700;color:white;line-height:1.2'>EHR–LIMS</div>
          <div style='font-size:10px;color:rgba(255,255,255,0.5)'>Validation Dashboard</div>
        </div>
      </div>
      <div style='display:flex;align-items:center;gap:6px;
                  background:rgba(255,255,255,0.08);border-radius:7px;padding:7px 10px'>
        <span style='font-size:13px'>📡</span>
        <div style='font-size:10px;color:rgba(255,255,255,0.7);line-height:1.4'>
          Live SharePoint · auto-refresh 5 min
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    if st.button("🔄  Refresh data", use_container_width=True):
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

    # ── FILTERS ───────────────────────────────────────────────────────────────
    all_districts = sorted(df['District'].unique())

    st.markdown("<p style='font-size:10px;font-weight:700;color:#475569;"
                "letter-spacing:0.8px;text-transform:uppercase;margin:0 0 10px'>Filters</p>",
                unsafe_allow_html=True)

    # ── Month range ───────────────────────────────────────────────────────────
    st.markdown("<p style='font-size:10px;font-weight:600;color:#64748B;margin:0 0 4px'>Month range</p>",
                unsafe_allow_html=True)
    col_m1, col_m2 = st.columns(2)
    m_start = col_m1.selectbox("From", MONTHS, index=0, label_visibility="collapsed")
    m_end   = col_m2.selectbox("To",   MONTHS, index=len(MONTHS)-1, label_visibility="collapsed")

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── District multiselect — empty = all ──────────────────────────────────
    sel_districts = st.multiselect(
        "District",
        options=all_districts,
        default=[],
        placeholder="All districts — type to filter…",
    )
    if not sel_districts:
        sel_districts = all_districts

    # ── Facility multiselect — empty = all ───────────────────────────────────
    fac_pool = sorted(df[df['District'].isin(sel_districts)]['Facility'].unique())
    sel_facilities = st.multiselect(
        "Facility",
        options=fac_pool,
        default=[],
        placeholder="All facilities — type to filter…",
    )
    if not sel_facilities:
        sel_facilities = fac_pool

    # ── Summary chip ──────────────────────────────────────────────────────────
    n_sel_fac    = len(sel_facilities)
    n_sel_months = len(MONTHS[MONTHS.index(m_start): MONTHS.index(m_end)+1])
    st.markdown(f"""
    <div style='margin-top:10px;background:white;border-radius:8px;
        border:1px solid #E2E8F0;padding:10px 12px;font-size:11px;
        color:#475569;line-height:2'>
        <b style='color:#1E3A5F'>{n_sel_fac}</b> facilities &nbsp;·&nbsp;
        <b style='color:#1E3A5F'>{n_sel_months}</b> months selected<br>
        <span style='color:#F59E0B'>●</span> Gap 1 — Paper vs EHR &nbsp;
        <span style='color:#EF4444'>●</span> Gap 2 — EHR vs SHR
    </div>""", unsafe_allow_html=True)


if df.empty:
    st.error("No data parsed. Check the file format.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# FILTER
# ─────────────────────────────────────────────────────────────────────────────
sel_months = MONTHS[MONTHS.index(m_start): MONTHS.index(m_end)+1]
dff = df[
    df['District'].isin(sel_districts) &
    df['Facility'].isin(sel_facilities) &
    df['Month'].isin(sel_months)
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
    border: 1px solid #DBEAFE;
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
.last-updated-lbl {{ font-size: 10px; color: #64748B; font-weight: 700; letter-spacing: 0.6px; text-transform: uppercase; }}
.last-updated-val {{ font-size: 13px; font-weight: 700; color: #0F172A; margin-top: 4px; }}

.replay-btn {{
    position: absolute; right: 0; top: 40px;
    background: #F0F7FF; border: 1px solid #E2E8F0; border-radius: 6px;
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
fac = dff.groupby(['District','Facility'], as_index=False).agg(
    Paper=('VL Paper (BAs)','sum'), EHR=('VL EHR (BAs)','sum'), SHR=('VL SHR (Jima)','sum')
)
fac['Gap1']   = fac['Paper'] - fac['EHR']
fac['Gap2']   = fac['EHR']   - fac['SHR']
fac['Gap1 %'] = (fac['Gap1']/fac['Paper']*100).round(1)
fac['Gap2 %'] = (fac['Gap2']/fac['EHR']*100).round(1)

# ─────────────────────────────────────────────────────────────────────────────
# MONTHLY CASCADE EXPLORER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('''<div style="font-size:14px;font-weight:600;color:#0D1B2A;
    margin:28px 0 14px;display:flex;align-items:center;gap:8px">
    📅 Monthly cascade explorer
    <span style="flex:1;height:1px;background:#E8EDF3;display:inline-block;margin-left:8px"></span>
</div>''', unsafe_allow_html=True)

# ── Build monthly summary ─────────────────────────────────────────────────────
MONTHS_ORDER = ['Oct-25','Nov-25','Dec-25','Jan-26','Feb-26','Mar-26','Apr-26']
monthly_all = dff.groupby('Month', as_index=False).agg(
    Paper=('VL Paper (BAs)', 'sum'),
    EHR  =('VL EHR (BAs)',   'sum'),
    SHR  =('VL SHR (Jima)',  'sum'),
    Facs =('Facility',        'nunique'),
)
monthly_all['Month'] = pd.Categorical(monthly_all['Month'], categories=MONTHS_ORDER, ordered=True)
monthly_all = monthly_all.sort_values('Month').reset_index(drop=True)
monthly_all['Gap1']    = monthly_all['Paper'] - monthly_all['EHR']
monthly_all['Gap2']    = monthly_all['EHR']   - monthly_all['SHR']
monthly_all['Gap1 %']  = (monthly_all['Gap1'] / monthly_all['Paper'] * 100).round(1)
monthly_all['Gap2 %']  = (monthly_all['Gap2'] / monthly_all['EHR']   * 100).round(1)
monthly_all['Capture %'] = (monthly_all['EHR'] / monthly_all['Paper'] * 100).round(1)
monthly_all['Submit %']  = (monthly_all['SHR'] / monthly_all['EHR']  * 100).round(1)

avail_months = [m for m in MONTHS_ORDER if m in monthly_all['Month'].values]

# ── Grouped bar chart — Paper / EHR / SHR by month ───────────────────────────
# Pre-compute per-month facility hover text (ordered by gap %)
_hover_paper = []   # Gap 1 breakdown on Paper bar
_hover_ehr   = []   # Gap 2 breakdown on EHR bar
_hover_shr   = []   # Gap 2 breakdown on SHR bar

for _m in monthly_all['Month']:
    _mf = dff[dff['Month'] == _m].copy()
    _mf['_g1']  = _mf['VL Paper (BAs)'] - _mf['VL EHR (BAs)']
    _mf['_g1p'] = np.where(_mf['VL Paper (BAs)']>0,
                           (_mf['_g1']/_mf['VL Paper (BAs)']*100).round(1), np.nan)
    _mf['_g2']  = _mf['VL EHR (BAs)'] - _mf['VL SHR (Jima)']
    _mf['_g2p'] = np.where(_mf['VL EHR (BAs)']>0,
                           (_mf['_g2']/_mf['VL EHR (BAs)']*100).round(1), np.nan)

    # Paper bar → show Gap 1 by facility
    _s1 = _mf.sort_values('_g1p', ascending=False).dropna(subset=['_g1p'])
    _h1 = (f'<b>Gap 1 — facilities ({_m})</b><br>'
           + '<br>'.join(
               f"{'🔴' if r['_g1p']>30 else '🟡' if r['_g1p']>10 else '🟢'} "
               f"{r['Facility']}: {int(r['_g1']):,} &nbsp;({r['_g1p']}%)"
               for _,r in _s1.iterrows()))
    _hover_paper.append(_h1)

    # EHR bar → show Gap 2 by facility
    _s2 = _mf.sort_values('_g2p', ascending=False).dropna(subset=['_g2p'])
    _h2 = (f'<b>Gap 2 — facilities ({_m})</b><br>'
           + '<br>'.join(
               f"{'🔴' if r['_g2p']>30 else '🟡' if r['_g2p']>10 else '🟢'} "
               f"{r['Facility']}: {int(r['_g2']):,} &nbsp;({r['_g2p']}%)"
               for _,r in _s2.iterrows()))
    _hover_ehr.append(_h2)
    _hover_shr.append(_h2)

fig_monthly_bar = go.Figure()

# Paper bars
fig_monthly_bar.add_bar(
    x=monthly_all['Month'], y=monthly_all['Paper'],
    name='Total VL Collected', marker_color='#1F7A4A',
    text=monthly_all['Paper'].apply(lambda v: f'{int(v):,}' if not pd.isna(v) else ''),
    textposition='outside', textfont=dict(size=9, color='#374151'),
    customdata=_hover_paper,
    hovertemplate='%{customdata}<extra></extra>',
)

# EHR bars
fig_monthly_bar.add_bar(
    x=monthly_all['Month'], y=monthly_all['EHR'],
    name='Captured in EHR', marker_color='#0891B2',
    text=monthly_all['EHR'].apply(lambda v: f'{int(v):,}' if not pd.isna(v) else ''),
    textposition='outside', textfont=dict(size=9, color='#374151'),
    customdata=_hover_ehr,
    hovertemplate='%{customdata}<extra></extra>',
)

# SHR bars
fig_monthly_bar.add_bar(
    x=monthly_all['Month'], y=monthly_all['SHR'],
    name='Submitted to SHR', marker_color='#2E5FA3',
    text=monthly_all['SHR'].apply(lambda v: f'{int(v):,}' if not pd.isna(v) else ''),
    textposition='outside', textfont=dict(size=9, color='#374151'),
    hovertemplate='<b>%{x}</b><br>Submitted to SHR: %{y:,.0f}<extra></extra>',
)

fig_monthly_bar.update_layout(
    barmode='group',
    height=400,
    margin=dict(l=10, r=10, t=70, b=10),
    legend=dict(
        orientation='h', yanchor='top', y=-0.08,
        xanchor='left', x=0,
        font=dict(size=11),
        bgcolor='rgba(0,0,0,0)',
    ),
    xaxis=dict(gridcolor='#EFF6FF', tickfont=dict(size=11)),
    yaxis=dict(gridcolor='#EFF6FF', title='Sample count', tickfont=dict(size=10)),
    plot_bgcolor='white', paper_bgcolor='white',
    hovermode='closest',
    hoverlabel=dict(
        bgcolor='white', bordercolor='#E2E8F0',
        font=dict(size=11, family='Inter, sans-serif'),
        align='left',
    ),
    title=dict(
        text=(
            '<b style="font-size:14px">Paper vs EHR vs SHR by month</b><br>'
            '<span style="font-size:11px;color:#64748B">'
            'Hover each bar to see facility breakdown ordered by gap %'
            '</span>'
        ),
        font=dict(size=14), x=0.01, y=0.97, yanchor='top',
        pad=dict(b=16),
    ),
)
st.plotly_chart(fig_monthly_bar, use_container_width=True)

# ── Auto-detect insights ──────────────────────────────────────────────────────
best_capture  = monthly_all.loc[monthly_all['Capture %'].idxmax()]
worst_capture = monthly_all.loc[monthly_all['Capture %'].idxmin()]
best_submit   = monthly_all.loc[monthly_all['Submit %'].idxmax()]
worst_submit  = monthly_all.loc[monthly_all['Submit %'].idxmin()]
highest_paper = monthly_all.loc[monthly_all['Paper'].idxmax()]
lowest_paper  = monthly_all.loc[monthly_all['Paper'].idxmin()]

# ── Insight banner ────────────────────────────────────────────────────────────
ic1, ic2, ic3, ic4 = st.columns(4)

def insight_card(col, icon, title, month, value, color, bg):
    col.markdown(f'''
    <div style="background:{bg};border-radius:10px;padding:14px 16px;
                border-left:4px solid {color};border:1px solid {color}30;">
        <div style="font-size:18px;margin-bottom:4px">{icon}</div>
        <div style="font-size:9px;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.6px;color:{color};margin-bottom:3px">{title}</div>
        <div style="font-size:15px;font-weight:800;color:#0F172A">{month}</div>
        <div style="font-size:11px;color:#64748B;margin-top:2px">{value}</div>
    </div>''', unsafe_allow_html=True)

insight_card(ic1, "🏆", "Best EHR capture",
             best_capture['Month'],
             f"{best_capture['Capture %']}% capture rate · {int(best_capture['EHR']):,} orders",
             "#059669", "#F0FDF4")
insight_card(ic2, "⚠️", "Worst EHR capture",
             worst_capture['Month'],
             f"{worst_capture['Capture %']}% capture rate · {int(worst_capture['Gap1']):,} missed",
             "#B45309", "#FFFBEB")
insight_card(ic3, "✅", "Best SHR submission",
             best_submit['Month'],
             f"{best_submit['Submit %']}% submission rate · {int(best_submit['SHR']):,} sent",
             "#2563EB", "#EFF6FF")
insight_card(ic4, "🔴", "Worst SHR submission",
             worst_submit['Month'],
             f"{worst_submit['Submit %']}% submission rate · {int(worst_submit['Gap2']):,} missed",
             "#B91C1C", "#FEF2F2")

# ── Month selector — tabs style ───────────────────────────────────────────────
sel_month = st.radio(
    "Select month",
    options=avail_months,
    index=len(avail_months)-1,
    horizontal=True,
    label_visibility="collapsed",
)

mrow = monthly_all[monthly_all['Month'] == sel_month].iloc[0]
avg_paper = monthly_all['Paper'].mean()
avg_ehr   = monthly_all['EHR'].mean()
avg_shr   = monthly_all['SHR'].mean()

# ── Facility breakdown — animated ranked bar charts ───────────────────────────
st.markdown(f'''<div style="font-size:14px;font-weight:600;color:#0D1B2A;
    margin:20px 0 12px;display:flex;align-items:center;gap:8px">
    Facility performance — {sel_month}
    <span style="flex:1;height:1px;background:#E8EDF3;display:inline-block;margin-left:8px"></span>
</div>''', unsafe_allow_html=True)

fac_month = dff[dff['Month'] == sel_month].copy()
fac_month['Gap1']   = fac_month['VL Paper (BAs)'] - fac_month['VL EHR (BAs)']
fac_month['Gap2']   = fac_month['VL EHR (BAs)']   - fac_month['VL SHR (Jima)']
fac_month['Gap1 %'] = (fac_month['Gap1'] / fac_month['VL Paper (BAs)'] * 100).round(1)
fac_month['Gap2 %'] = (fac_month['Gap2'] / fac_month['VL EHR (BAs)']  * 100).round(1)

def _bar_color(pct):
    if pd.isna(pct) or pct < 0: return '#3B82F6'
    if pct > 30: return '#EF4444'
    if pct > 10: return '#F59E0B'
    return '#10B981'

def _build_animated_chart(df, val_col, pct_col, abs_col, title, subtitle):
    """Build a Plotly figure that reveals bars one-by-one, worst first."""
    s = df.dropna(subset=[pct_col]).sort_values(pct_col, ascending=False)
    s = s.reset_index(drop=True)

    # Guard: if no valid rows, return an empty placeholder figure
    if s.empty:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text=f'<b>{title}</b>', font=dict(size=13), x=0.01),
            height=200, plot_bgcolor='white', paper_bgcolor='white',
            annotations=[dict(text='No data available for selected filters',
                              xref='paper', yref='paper', x=0.5, y=0.5,
                              showarrow=False, font=dict(size=13, color='#64748B'))],
        )
        return fig

    facs   = s['Facility'].tolist()
    pcts   = s[pct_col].tolist()
    absv   = s[abs_col].tolist()
    colors = [_bar_color(p) for p in pcts]

    n = len(facs)
    # Each frame reveals one more bar (worst → best)
    frames = []
    for i in range(n + 1):
        bar_x    = pcts[:i]  + [0]*(n-i)
        bar_text = [f'{absv[j]:,.0f}  ({pcts[j]}%)' for j in range(i)] + ['']*( n-i)
        frames.append(go.Frame(
            data=[go.Bar(
                x=bar_x, y=facs,
                orientation='h',
                marker_color=colors,
                text=bar_text,
                textposition='outside',
                textfont=dict(size=10, color='#374151'),
                cliponaxis=False,
                width=0.6,
            )],
            name=str(i)
        ))

    fig = go.Figure(
        data=[go.Bar(
            x=[0]*n, y=facs,
            orientation='h',
            marker_color=colors,
            text=['']*n,
            textposition='outside',
            cliponaxis=False,
            width=0.6,
        )],
        frames=frames,
    )
    fig.update_layout(
        title=dict(
            text=f'<b>{title}</b><br>'
                 f'<span style="font-size:11px;color:#64748B">{subtitle}</span>',
            font=dict(size=13), x=0.01
        ),
        height=max(360, n * 42 + 90),
        margin=dict(l=160, r=180, t=72, b=20),
        xaxis=dict(
            title=None,
            ticksuffix='%',
            gridcolor='#EFF6FF', zeroline=True,
            zerolinecolor='#CBD5E1', zerolinewidth=1.5,
            showline=True, linecolor='#CBD5E1', linewidth=1,
            range=[-5, max((max(pcts) if pcts else 0) + 25, 20)],
        ),
        yaxis=dict(
            autorange='reversed',
            tickfont=dict(size=11),
            tickmode='array', tickvals=facs, ticktext=facs,
        ),
        plot_bgcolor='white', paper_bgcolor='white',
        showlegend=False,
        updatemenus=[dict(
            type='buttons', showactive=False,
            visible=False,
            buttons=[dict(
                label='Play',
                method='animate',
                args=[None, dict(
                    frame=dict(duration=120, redraw=True),
                    fromcurrent=True,
                    mode='immediate',
                    transition=dict(duration=80, easing='cubic-in-out'),
                )]
            )]
        )],
    )
    return fig

_g1_chart = _build_animated_chart(
    fac_month, 'VL EHR (BAs)', 'Gap1 %', 'Gap1',
    'Gap 1 — Paper vs EHR (samples not entered into EHR)',
    f'Worst → best · {sel_month} · bars animate in order of severity'
)
_g2_chart = _build_animated_chart(
    fac_month, 'VL SHR (Jima)', 'Gap2 %', 'Gap2',
    'Gap 2 — EHR vs SHR (orders not submitted to SHR)',
    f'Worst → best · {sel_month} · bars animate in order of severity'
)

import plotly.io as _pio

def _animated_chart_html(fig, chart_id):
    """Convert Plotly figure to self-contained HTML that auto-plays."""
    html = _pio.to_html(
        fig, include_plotlyjs='cdn',
        div_id=chart_id, full_html=False,
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
st.markdown('<div style="font-size:14px;font-weight:600;color:#0D1B2A;margin:28px 0 12px;display:flex;align-items:center;gap:8px">📊 Data leakage by facility<span style="flex:1;height:1px;background:#E8EDF3;display:inline-block;margin-left:8px"></span></div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)

def styled_bar(df_in, bg_col, fg_col, bg_name, fg_name, gap_col, gap_pct_col, title, subtitle):
    # Sort by gap % worst first
    s = df_in.sort_values(gap_pct_col, ascending=True).copy()
    s = s.reset_index(drop=True)

    pcts  = s[gap_pct_col].fillna(0).tolist()
    abs_v = s[fg_col].fillna(0).tolist()
    facs  = s['Facility'].tolist()

    colors = []
    for v in pcts:
        if v < 0:    colors.append('#1D4ED8')
        elif v > 30: colors.append('#EF4444')
        elif v > 10: colors.append('#F59E0B')
        else:        colors.append('#10B981')

    fig = go.Figure()
    # Background bar (max reference = 100%)
    fig.add_bar(
        y=facs, x=[100]*len(facs), name=bg_name,
        orientation='h', marker_color='#DBEAFE', opacity=0.4,
        hoverinfo='skip', showlegend=False,
    )
    # Gap % bar
    fig.add_bar(
        y=facs, x=[abs(p) for p in pcts], name=fg_name,
        orientation='h', marker_color=colors,
        text=[f'{int(abs(v)):,}  ({abs(p):.1f}%)' for v, p in zip(abs_v, pcts)],
        textposition='outside', textfont=dict(size=9, color='#374151'),
        customdata=list(zip(abs_v, pcts)),
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Absolute gap: %{customdata[0]:,.0f}<br>'
            'Gap %: %{customdata[1]:.1f}%'
            '<extra></extra>'
        ),
    )
    fig.update_layout(
        title=dict(
            text=(
                f'<b>{title}</b><br>'
                f'<span style="font-size:10px;color:#64748B">'
                f'Worst → best &nbsp;·&nbsp; '
                f'<span style="color:#EF4444">■ >30%</span> &nbsp;'
                f'<span style="color:#F59E0B">■ 10–30%</span> &nbsp;'
                f'<span style="color:#10B981">■ <10%</span> &nbsp;'
                f'<span style="color:#1D4ED8">■ EHR > Paper</span>'
                f'</span>'
            ),
            font=dict(size=13), x=0,
        ),
        barmode='overlay',
        height=max(420, len(facs) * 30 + 120),
        margin=dict(l=10, r=90, t=72, b=20),
        showlegend=False,
        xaxis=dict(
            range=[0, 110],
            tickvals=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            ticktext=['0%','10%','20%','30%','40%','50%','60%','70%','80%','90%','100%'],
            gridcolor='#EFF6FF', tickfont=dict(size=10),
            showline=True, linecolor='#CBD5E1',
        ),
        yaxis=dict(tickfont=dict(size=10, color='#374151')),
        plot_bgcolor='white', paper_bgcolor='white',
    )
    return fig

with col_a:
    st.plotly_chart(
        styled_bar(fac, 'Paper','EHR','Total VL Collected','EHR Captured',
                   'Gap1','Gap1 %','Gap 1 — Paper vs EHR',
                   'Colour = severity: red >30% · amber 10–30% · green <10%'),
        use_container_width=True)

with col_b:
    st.plotly_chart(
        styled_bar(fac, 'EHR','SHR','EHR (BAs)','SHR Submitted',
                   'Gap2','Gap2 %','Gap 2 — EHR vs SHR',
                   'Colour = severity: red >30% · amber 10–30% · green <10%'),
        use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# LEADERBOARD + DRILLDOWN + TREND (combined)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-hdr">🏆 Leakage leaderboard & facility drilldown</div>',
            unsafe_allow_html=True)

col_lb, col_drill, col_funnel = st.columns([1.3, 1, 0.75])

with col_lb:
    board = fac.sort_values('Gap1 %', ascending=False).reset_index(drop=True)

    def badge(pct, ehr_val=None, is_gap2=False):
        if is_gap2 and ehr_val is not None and ehr_val == 0:
            return '<span class="lb-badge badge-grey">No EHR data</span>'
        if pd.isna(pct):  return f'<span class="lb-badge badge-grey">N/A</span>'
        if pct < 0:       return f'<span class="lb-badge badge-blue">{pct:.1f}% ↑</span>'
        if pct > 30:      return f'<span class="lb-badge badge-red">{pct:.1f}%</span>'
        if pct > 10:      return f'<span class="lb-badge badge-amber">{pct:.1f}%</span>'
        return                   f'<span class="lb-badge badge-green">{pct:.1f}%</span>'

    def mini_bar(ehr, paper, color):
        pct = min(ehr/paper*100, 100) if paper > 0 else 0
        return f"""<div style="background:#EFF6FF;border-radius:4px;height:6px;width:100%">
            <div style="background:{color};height:6px;border-radius:4px;width:{pct:.0f}%"></div>
        </div>"""

    def auto_insight(row):
        """Generate plain-language finding for a facility."""
        fac   = row['Facility']
        paper = row['Paper']
        ehr   = row['EHR']
        shr   = row['SHR']
        g1    = row['Gap1']
        g1p   = row['Gap1 %'] if not pd.isna(row['Gap1 %']) else 0
        g2    = row['Gap2']
        g2p   = row['Gap2 %'] if not pd.isna(row['Gap2 %']) else 0
        parts = []

        # ── Gap 1 finding ─────────────────────────────────────────────────────
        if ehr == 0 and paper > 0:
            parts.append(
                f"🚫 <b>No EHR entries at all.</b> "
                f"{int(paper):,} samples were collected on paper but none were recorded in the EHR system. "
                f"That is a 100% gap — the site is not using the digital system."
            )
        elif g1p > 30:
            parts.append(
                f"⚠️ <b>{g1p:.1f}% of paper samples were not recorded in EHR.</b> "
                f"Only {int(ehr):,} of {int(paper):,} samples made it into the digital record — "
                f"{int(g1):,} samples exist on paper but not in EHR."
            )
        elif g1p < 0:
            parts.append(
                f"🔵 <b>EHR has {abs(g1p):.1f}% more entries than paper records.</b> "
                f"EHR shows {int(ehr):,} orders but only {int(paper):,} were collected on paper. "
                f"The extra {int(abs(g1)):,} entries may be duplicates — worth investigating."
            )
        elif g1p <= 10:
            parts.append(
                f"✅ <b>Only {g1p:.1f}% of paper samples were not captured in EHR.</b> "
                f"{int(ehr):,} of {int(paper):,} samples recorded — this site is performing well on EHR capture."
            )
        else:
            parts.append(
                f"🟡 <b>{g1p:.1f}% of paper samples were not recorded in EHR.</b> "
                f"{int(g1):,} of {int(paper):,} samples are missing from the digital record."
            )

        # ── Gap 2 finding ─────────────────────────────────────────────────────
        if ehr == 0:
            parts.append(
                "🔗 <b>SHR submission is not possible.</b> "
                "With no EHR data there is nothing to send to the national SHR system."
            )
        elif shr == 0 and ehr > 0:
            parts.append(
                f"🚨 <b>100% of EHR orders were never submitted to SHR.</b> "
                f"{int(ehr):,} records exist in EHR but none have ever reached SHR. "
                f"The EHR-to-SHR link appears completely broken — this needs urgent technical attention."
            )
        elif g2p > 30:
            parts.append(
                f"⚠️ <b>{g2p:.1f}% of EHR orders were not submitted to SHR.</b> "
                f"{int(g2):,} of {int(ehr):,} records did not reach SHR — "
                f"only {int(shr):,} were successfully submitted."
            )
        elif g2p < 0:
            parts.append(
                f"🔵 <b>SHR shows {abs(g2p):.1f}% more than EHR.</b> "
                f"{int(shr):,} SHR records vs {int(ehr):,} EHR orders — "
                f"some data may be reaching SHR from outside the EHR system."
            )
        else:
            parts.append(
                f"✅ <b>Only {g2p:.1f}% of EHR orders did not reach SHR.</b> "
                f"{int(shr):,} of {int(ehr):,} orders were successfully submitted — "
                f"SHR submission is working well at this site."
            )

        return "<br><br>".join(parts)

    html_rows = ""
    for i, row in board.iterrows():
        critical = ' critical' if (not pd.isna(row['Gap1 %']) and row['Gap1 %'] > 30) else ''
        g1_pct_val = row['Gap1 %'] if not pd.isna(row['Gap1 %']) else 0
        if g1_pct_val > 30:
            rank_icon = '⚠️'
        elif g1_pct_val > 10:
            rank_icon = f'#{i+1}'
        else:
            rank_icon = ['🥇','🥈','🥉'][i] if i < 3 else f'#{i+1}'

        insight_html = auto_insight(row)
        fac_id = row['Facility'].replace(' ','_').replace("'","")

        html_rows += f"""
        <div class="lb-row{critical}">
          <div class="lb-rank">{rank_icon}</div>
          <div class="lb-name">
            <div class="lbn-fac">{row['Facility']}</div>
            <div class="lbn-dist">{row['District']}</div>
          </div>
          <div class="lb-bars" style="font-size:11px;color:#374151">
            Gap 1: {badge(row['Gap1 %'])} &nbsp; Gap 2: {badge(row['Gap2 %'], ehr_val=row['EHR'], is_gap2=True)}
            <div style="margin-top:5px">{mini_bar(row['EHR'], row['Paper'], '#10B981')}</div>
            <div style="font-size:9px;color:#64748B;margin-top:2px">EHR capture rate</div>
          </div>
          <div class="lb-info">
            <button class="info-btn" onclick="toggleInsight('{fac_id}', '{row['Facility']}', '{row['District']}')"
                    title="View finding">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="7" cy="7" r="6.25" stroke="#3B82F6" stroke-width="1.5"/>
                <rect x="6.25" y="6" width="1.5" height="4.5" rx="0.75" fill="#3B82F6"/>
                <circle cx="7" cy="3.75" r="0.85" fill="#3B82F6"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="insight-panel" id="ins_{fac_id}">
          <div class="insight-body">{insight_html}</div>
        </div>"""

    components.html(f"""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    * {{ font-family: 'Inter', sans-serif; box-sizing: border-box; }}
    .lb-row {{ display:flex;align-items:center;padding:10px 14px;border-radius:10px;
               margin-bottom:2px;gap:12px;background:#F5F9FF;
               border:1px solid #DBEAFE;transition:background 0.15s; }}
    .lb-row:hover {{ background:#EFF6FF; }}
    .lb-rank {{ font-size:13px;font-weight:700;color:#64748B;min-width:28px; }}
    .lb-name {{ flex:1; }}
    .lbn-fac {{ font-size:13px;font-weight:600;color:#0D1B2A; }}
    .lbn-dist {{ font-size:11px;color:#475569;font-weight:500; }}
    .lb-bars {{ flex:0 0 190px; }}
    .lb-info {{ flex:0 0 28px;text-align:center; }}
    .info-btn {{
        background:#EFF6FF;border:1.5px solid #BFDBFE;
        cursor:pointer;padding:0;
        border-radius:50%;width:26px;height:26px;
        display:flex;align-items:center;justify-content:center;
        transition:background 0.15s,border-color 0.15s,transform 0.15s;
        flex-shrink:0;
    }}
    .info-btn:hover {{
        background:#DBEAFE;border-color:#93C5FD;transform:scale(1.1);
    }}
    .info-btn svg {{ display:block; }}
    .lb-badge {{ font-size:11px;font-weight:700;border-radius:20px;padding:2px 9px;white-space:nowrap; }}
    .badge-red    {{ background:#FFF1F2;color:#BE123C;border:1px solid #FECDD3; }}
    .badge-amber  {{ background:#FFFBEB;color:#B45309;border:1px solid #FDE68A; }}
    .badge-green  {{ background:#F0FDF4;color:#15803D;border:1px solid #BBF7D0; }}
    .badge-purple {{ background:#F5F3FF;color:#6D28D9;border:1px solid #DDD6FE; }}
    .badge-grey   {{ background:#EFF6FF;color:#64748B;border:1px solid #CBD5E1;font-style:italic; }}
    .badge-blue   {{ background:#EFF6FF;color:#1D4ED8;border:1px solid #BFDBFE;font-weight:700; }}

    /* insight panel — hidden data store */
    .insight-panel {{ display:none; }}

    @keyframes pulse-red {{
      0%,100% {{ box-shadow:0 0 0 0 rgba(239,68,68,0); }}
      50%      {{ box-shadow:0 0 0 6px rgba(239,68,68,0.15); }}
    }}
    .critical {{ animation:pulse-red 2.5s ease-in-out infinite;
                 border-color:#FECDD3!important;background:#FFF5F5!important; }}

    /* Modal overlay */
    .modal-overlay {{
        display:none;position:fixed;inset:0;
        background:rgba(15,23,42,0.5);
        z-index:9999;
        animation:fadeIn 0.15s ease;
    }}
    .modal-overlay.open {{
        display:flex;align-items:center;justify-content:center;
    }}
    @keyframes fadeIn {{ from{{opacity:0}} to{{opacity:1}} }}
    .modal-box {{
        background:white;border-radius:14px;
        padding:24px 26px 22px;
        max-width:400px;width:88%;
        box-shadow:0 24px 64px rgba(0,0,0,0.3);
        position:relative;
        animation:popUp 0.2s cubic-bezier(0.34,1.56,0.64,1);
    }}
    @keyframes popUp {{
        from{{opacity:0;transform:scale(0.85)}}
        to  {{opacity:1;transform:scale(1)}}
    }}
    .modal-close {{
        position:absolute;top:12px;right:14px;
        background:#F1F5F9;border:none;border-radius:50%;
        width:26px;height:26px;font-size:14px;
        cursor:pointer;color:#64748B;
        display:flex;align-items:center;justify-content:center;
        transition:background 0.1s;
    }}
    .modal-close:hover {{ background:#E2E8F0;color:#0F172A; }}
    .modal-fac  {{ font-size:15px;font-weight:700;color:#0D1B2A;margin-bottom:3px; }}
    .modal-dist {{ font-size:11px;color:#64748B;margin-bottom:12px; }}
    .modal-hr   {{ height:1px;background:#E8EDF3;margin-bottom:14px; }}
    .modal-body {{ font-size:13px;color:#374151;line-height:1.9; }}
    .modal-body b {{ color:#0F172A; }}
    </style>

    <!-- Single shared modal -->
    <div class="modal-overlay" id="insight-modal" onclick="if(event.target===this)closeModal()">
      <div class="modal-box">
        <button class="modal-close" onclick="closeModal()">✕</button>
        <div class="modal-fac"  id="modal-fac"></div>
        <div class="modal-dist" id="modal-dist"></div>
        <div class="modal-hr"></div>
        <div class="modal-body" id="modal-body"></div>
      </div>
    </div>

    <script>
    function toggleInsight(id, fac, dist) {{
        var panel = document.getElementById('ins_' + id);
        if (!panel) return;
        document.getElementById('modal-fac').textContent  = fac;
        document.getElementById('modal-dist').textContent = dist;
        document.getElementById('modal-body').innerHTML   = panel.innerHTML;
        document.getElementById('insight-modal').classList.add('open');
    }}
    function closeModal() {{
        document.getElementById('insight-modal').classList.remove('open');
    }}
    </script>

    <div>{html_rows}</div>
    """, height=min(88 * len(board) + 20, 560), scrolling=True)

with col_drill:
    # ── Facility drilldown ─────────────────────────────────────────────────────
    _fac_options = ['⭐ All sites (combined)'] + sorted(dff['Facility'].unique())
    sel_fac = st.selectbox("Select facility", _fac_options,
                           label_visibility="collapsed")

    _all_sites = sel_fac == '⭐ All sites (combined)'
    fac_df = (
        dff.groupby('Month', as_index=False).agg(
            {'VL Paper (BAs)':'sum','VL EHR (BAs)':'sum','VL SHR (Jima)':'sum',
             'Month Date':'first','Activation Date':'first'}
        ).sort_values('Month Date')
        if _all_sites
        else dff[dff['Facility'] == sel_fac].sort_values('Month Date')
    )
    if not _all_sites:
        fac_df['Gap1']   = fac_df['VL Paper (BAs)'] - fac_df['VL EHR (BAs)']
        fac_df['Gap2']   = fac_df['VL EHR (BAs)']   - fac_df['VL SHR (Jima)']
        fac_df['Gap1 %'] = (fac_df['Gap1']/fac_df['VL Paper (BAs)']*100).round(1)
        fac_df['Gap2 %'] = (fac_df['Gap2']/fac_df['VL EHR (BAs)']*100).round(1)

    act  = None if _all_sites else (fac_df['Activation Date'].iloc[0] if not fac_df.empty else None)
    dist = f"All {dff['District'].nunique()} districts" if _all_sites else (fac_df['District'].iloc[0] if not fac_df.empty else '—')
    g1   = (dff['VL Paper (BAs)'].sum() - dff['VL EHR (BAs)'].sum()) if _all_sites else fac_df['Gap1'].sum()
    g2   = (dff['VL EHR (BAs)'].sum()   - dff['VL SHR (Jima)'].sum()) if _all_sites else fac_df['Gap2'].sum()
    g1p  = (g1 / dff['VL Paper (BAs)'].sum() * 100) if _all_sites else fac_df['Gap1 %'].mean()
    g2p  = (g2 / dff['VL EHR (BAs)'].sum()   * 100) if _all_sites else fac_df['Gap2 %'].mean()
    chart_title = 'All facilities — combined trend' if _all_sites else f'{sel_fac} — monthly trend'

    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown(f"""<div class="drill-stat">
            <div class="ds-lbl">{'Scope' if _all_sites else 'District'}</div>
            <div class="ds-val" style="font-size:14px">{dist}</div>
        </div>
        <div class="drill-stat">
            <div class="ds-lbl">Gap 1 — Paper vs EHR</div>
            <div class="ds-val" style="color:#F59E0B">{int(g1):,} <span style="font-size:12px">({g1p:.1f}%)</span></div>
        </div>""", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""<div class="drill-stat">
            <div class="ds-lbl">{'Sites' if _all_sites else 'Activated'}</div>
            <div class="ds-val" style="font-size:14px">{f"{dff['Facility'].nunique()} facilities" if _all_sites else (act.strftime('%b %Y') if act else '—')}</div>
        </div>
        <div class="drill-stat">
            <div class="ds-lbl">Gap 2 — EHR vs SHR</div>
            <div class="ds-val" style="color:#EF4444">{int(g2):,} <span style="font-size:12px">({g2p:.1f}%)</span></div>
        </div>""", unsafe_allow_html=True)

    # Facility / combined trend
    fig_drill = go.Figure()
    fig_drill.add_scatter(x=fac_df['Month'], y=fac_df['VL Paper (BAs)'],
        name='Total VL Collected',
        mode='lines+markers', line=dict(color='#1F7A4A',width=2.5),
        marker=dict(size=8,color='white',line=dict(color='#1F7A4A',width=2)),
        fill=None)
    fig_drill.add_scatter(x=fac_df['Month'], y=fac_df['VL EHR (BAs)'],
        name='EHR Captured',
        mode='lines+markers', line=dict(color='#0891B2',width=2.5),
        marker=dict(size=8,color='white',line=dict(color='#0891B2',width=2)),
        fill='tonexty', fillcolor='rgba(31,122,74,0.07)')
    fig_drill.add_scatter(x=fac_df['Month'], y=fac_df['VL SHR (Jima)'],
        name='SHR Submitted',
        mode='lines+markers', line=dict(color='#2E5FA3',width=2.5),
        marker=dict(size=8,color='white',line=dict(color='#2E5FA3',width=2)),
        fill='tonexty', fillcolor='rgba(8,145,178,0.07)')
    fig_drill.update_layout(
        title=dict(text=f'<b>{chart_title}</b>',
                   font=dict(size=12), x=0.01),
        height=280, margin=dict(l=10,r=10,t=60,b=50),
        legend=dict(orientation='h', yanchor='top', y=-0.18,
                    font=dict(size=9)),
        xaxis=dict(gridcolor='#EFF6FF',tickfont=dict(size=9)),
        yaxis=dict(gridcolor='#EFF6FF',tickfont=dict(size=9)),
        plot_bgcolor='white', paper_bgcolor='white', hovermode='x unified',
    )
    st.plotly_chart(fig_drill, use_container_width=True)

with col_funnel:
    st.markdown('<div style="font-size:12px;font-weight:600;color:#0D1B2A;'
                'margin-bottom:8px">📊 Pipeline retention</div>',
                unsafe_allow_html=True)

    # Funnel responds to facility selection
    if _all_sites:
        _fp, _fe, _fs = int(total_paper), int(total_ehr), int(total_shr)
        _funnel_lbl = 'All facilities'
    else:
        _fd = dff[dff['Facility'] == sel_fac]
        _fp = int(_fd['VL Paper (BAs)'].sum())
        _fe = int(_fd['VL EHR (BAs)'].sum())
        _fs = int(_fd['VL SHR (Jima)'].sum())
        _funnel_lbl = sel_fac

    fig_funnel = go.Figure(go.Funnel(
        y=['Paper collected', 'Captured in EHR', 'Submitted to SHR'],
        x=[_fp, _fe, _fs],
        textinfo='value+percent initial',
        textfont=dict(size=11),
        marker=dict(
            color=['#1F7A4A', '#0891B2', '#2E5FA3'],
            line=dict(color='white', width=2)
        ),
        connector=dict(line=dict(color='#DBEAFE', width=1)),
    ))
    fig_funnel.update_layout(
        title=dict(text=f'<b style="font-size:11px">{_funnel_lbl}</b>',
                   font=dict(size=11), x=0.02),
        height=380,
        margin=dict(l=10, r=10, t=34, b=10),
        paper_bgcolor='white', plot_bgcolor='white',
        showlegend=False,
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

    _cap = round(_fe/_fp*100,1) if _fp > 0 else 0
    _sub = round(_fs/_fe*100,1) if _fe > 0 else 0
    _ret = round(_fs/_fp*100,1) if _fp > 0 else 0
    st.markdown(f"""
    <div style="background:#F0F7FF;border-radius:10px;padding:12px 14px;
                border:1px solid #DBEAFE;font-size:11px;line-height:2.3;">
        <div style="display:flex;justify-content:space-between">
            <span style="color:#475569">EHR capture rate</span>
            <b style="color:#0891B2">{_cap}%</b>
        </div>
        <div style="display:flex;justify-content:space-between">
            <span style="color:#475569">SHR submission rate</span>
            <b style="color:#2E5FA3">{_sub}%</b>
        </div>
        <div style="display:flex;justify-content:space-between">
            <span style="color:#475569">Overall retention</span>
            <b style="color:#1E3A5F">{_ret}%</b>
        </div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""<div style="text-align:center;margin-top:32px;padding:16px;
    color:#64748B;font-size:11px;border-top:1px solid #E8EDF3;">
    🔴 >30% gap · 🟡 10–30% · 🟢 &lt;10% &nbsp;|&nbsp;
    Analysis starts the month <i>after</i> facility go-live &nbsp;|&nbsp;
    Zim-TTECH · EHR–LIMS Validation
</div>""", unsafe_allow_html=True)
