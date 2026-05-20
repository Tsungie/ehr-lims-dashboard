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
    layout="wide", page_icon="🏥",
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

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 8px'>
        <div style='font-size:18px;font-weight:700;color:white'>🏥 EHR–LIMS</div>
        <div style='font-size:11px;color:rgba(255,255,255,0.4);margin-top:2px'>Validation Dashboard</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

    # Source indicator
    st.markdown("""<div style='font-size:10px;color:rgba(255,255,255,0.45);margin-bottom:4px;
                              font-weight:600;letter-spacing:0.5px'>DATA SOURCE</div>
        <div style='display:flex;align-items:center;gap:6px;background:rgba(255,255,255,0.06);
                    border-radius:8px;padding:8px 10px;margin-bottom:4px'>
            <span style='font-size:14px'>📡</span>
            <div>
                <div style='font-size:11px;font-weight:600;color:rgba(255,255,255,0.85)'>
                    Live SharePoint Excel
                </div>
                <div style='font-size:10px;color:rgba(255,255,255,0.35);margin-top:1px'>
                    Auto-refreshes every 5 min
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    if st.button("🔄  Refresh now", use_container_width=True):
        fetch_sharepoint.clear()
        st.rerun()

    st.markdown("---")

    # Load data from SharePoint
    with st.spinner("Fetching live data from SharePoint…"):
        try:
            file_bytes = fetch_sharepoint(SHAREPOINT_URL)
            sp_ok = True
        except Exception as sp_err:
            sp_ok = False
            sp_error = str(sp_err)

    if not sp_ok:
        st.error(f"Could not reach SharePoint: {sp_error}")
        st.markdown("""<div style='font-size:10px;color:rgba(255,255,255,0.4);margin-top:8px'>
            The sharing link may need to be set to<br>
            <b>"Anyone with the link"</b> in SharePoint,<br>
            or your network may be blocking the request.
        </div>""", unsafe_allow_html=True)
        st.stop()

    df = load_data(file_bytes)

    districts  = sorted(df['District'].unique())
    fac_pool   = sorted(df['Facility'].unique())

    st.markdown("<div style='font-size:10px;font-weight:600;color:rgba(255,255,255,0.45);letter-spacing:0.5px;margin-bottom:6px'>DISTRICT</div>",
                unsafe_allow_html=True)
    sel_districts = st.multiselect("Districts", districts, default=districts,
                                   label_visibility="collapsed")

    fac_pool = sorted(df[df['District'].isin(sel_districts)]['Facility'].unique())
    st.markdown("<div style='font-size:10px;font-weight:600;color:rgba(255,255,255,0.45);letter-spacing:0.5px;margin-top:12px;margin-bottom:6px'>FACILITY</div>",
                unsafe_allow_html=True)
    sel_facilities = st.multiselect("Facilities", fac_pool, default=fac_pool,
                                    label_visibility="collapsed")

    st.markdown("<div style='font-size:10px;font-weight:600;color:rgba(255,255,255,0.45);letter-spacing:0.5px;margin-top:12px;margin-bottom:6px'>MONTH RANGE</div>",
                unsafe_allow_html=True)
    m_start = st.selectbox("From", MONTHS, index=0, label_visibility="collapsed")
    m_end   = st.selectbox("To",   MONTHS, index=len(MONTHS)-1, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("""<div style='font-size:10px;color:rgba(255,255,255,0.35);line-height:2'>
        🟡 <b>Gap 1</b> — Paper vs EHR<br>
        🔴 <b>Gap 2</b> — EHR vs SHR<br>
        Analysis starts month after go-live
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



<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
* {{ box-sizing:border-box; margin:0; padding:0; font-family:'Inter',sans-serif; }}
body {{ background:transparent; }}

/* ── header ── */
.header {{
  display:flex; justify-content:space-between; align-items:center;
  padding-bottom:14px; margin-bottom:18px; border-bottom:1px solid #E2E8F0;
}}
.h-left  {{ display:flex; align-items:center; gap:12px; }}
.h-icon  {{ width:42px; height:42px; border-radius:10px; background:#1E3A5F;
            display:flex; align-items:center; justify-content:center; font-size:20px; }}
.h-title {{ font-size:17px; font-weight:700; color:#0F172A; }}
.h-sub   {{ font-size:11px; color:#64748B; margin-top:2px; }}
.h-tags  {{ display:flex; gap:5px; margin-top:6px; }}
.h-tag   {{ font-size:10px; font-weight:600; border-radius:4px; padding:2px 8px;
            background:#F1F5F9; color:#475569; border:1px solid #E2E8F0;
            display:inline-flex; align-items:center; gap:4px; }}
.live-dot {{ width:5px; height:5px; border-radius:50%; background:#22C55E;
             box-shadow:0 0 4px rgba(34,197,94,0.8); animation:blink 2s infinite; }}
@keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:0.15}} }}
.h-right  {{ text-align:right; }}
.h-ts-lbl {{ font-size:8px; font-weight:700; color:#94A3B8; letter-spacing:1.2px; text-transform:uppercase; }}
.h-ts-val {{ font-size:13px; font-weight:700; color:#0F172A; margin-top:2px; }}

/* ── stage ── */
.stage {{
  background:#F8FAFC; border:1px solid #E8EDF3; border-radius:14px;
  padding:28px 24px 32px; margin-bottom:14px; position:relative;
}}
.replay-btn {{
  position:absolute; top:12px; right:14px;
  font-size:10px; font-weight:600; color:#64748B;
  background:white; border:1px solid #E2E8F0; border-radius:6px;
  padding:4px 10px; cursor:pointer; transition:all 0.15s; z-index:10;
}}
.replay-btn:hover {{ background:#F1F5F9; color:#0F172A; }}

/* ── flow row ── */
.flow-row {{
  display:flex; align-items:flex-start; gap:0;
}}

/* ── node card ── */
.node {{
  flex:1; background:white; border-radius:12px;
  border:1px solid #E2E8F0; border-top:4px solid;
  padding:20px 16px 18px; text-align:center;
  box-shadow:0 2px 8px rgba(0,0,0,0.06);
  opacity:0; transform:translateY(16px) scale(0.97);
  transition:opacity 0.5s ease, transform 0.5s ease, box-shadow 0.15s;
}}
.node.show {{ opacity:1; transform:translateY(0) scale(1); }}
.node.show:hover {{ box-shadow:0 6px 18px rgba(0,0,0,0.1); transform:translateY(-2px); }}
.n-paper  {{ border-top-color:#059669; }}
.n-ehr    {{ border-top-color:#0F766E; }}
.n-shr    {{ border-top-color:#1E3A5F; }}
.node-icon {{ font-size:24px; margin-bottom:12px; }}
.node-val  {{ font-size:26px; font-weight:800; letter-spacing:-0.5px; line-height:1; }}
.n-paper .node-val {{ color:#059669; }}
.n-ehr   .node-val {{ color:#0F766E; }}
.n-shr   .node-val {{ color:#1E3A5F; }}
.node-lbl {{ font-size:10px; font-weight:700; text-transform:uppercase;
             letter-spacing:0.6px; color:#64748B; margin-top:7px; }}
.node-sub {{ font-size:9px; color:#94A3B8; margin-top:3px; }}

/* ── connector ── */
.connector {{
  flex:0 0 110px; display:flex; flex-direction:column;
  align-items:center; padding-top:44px; position:relative;
}}

/* horizontal arrow */
.arrow-track {{
  width:100%; height:2px; background:#CBD5E1; position:relative;
  clip-path:inset(0 100% 0 0);
  transition:clip-path 0.6s cubic-bezier(0.4,0,0.2,1);
}}
.arrow-track.show {{ clip-path:inset(0 0% 0 0); }}
.arrow-track::after {{
  content:''; position:absolute; right:-1px; top:-5px;
  border:6px solid transparent; border-left:8px solid #CBD5E1;
}}

/* vertical drop line */
.drop-wrap {{
  display:flex; flex-direction:column; align-items:center;
  margin-top:12px; opacity:0; transform:translateY(-8px);
  transition:opacity 0.4s ease, transform 0.4s ease;
}}
.drop-wrap.show {{ opacity:1; transform:translateY(0); }}
.drop-line {{
  width:2.5px; background:linear-gradient(to bottom, var(--dc), rgba(0,0,0,0.05));
  border-radius:2px;
  transform:scaleY(0); transform-origin:top;
  transition:transform 0.5s cubic-bezier(0.4,0,0.2,1);
}}
.drop-line.show {{ transform:scaleY(1); }}

/* gap card */
.gap-card {{
  background:white; border-radius:10px; border:1px solid;
  padding:10px 14px; text-align:center; min-width:108px;
  box-shadow:0 2px 8px rgba(0,0,0,0.07);
  opacity:0; transform:scale(0.85) translateY(-6px);
  transition:opacity 0.4s ease, transform 0.4s cubic-bezier(0.34,1.4,0.64,1);
}}
.gap-card.show {{ opacity:1; transform:scale(1) translateY(0); }}
.gap-type {{ font-size:8px; font-weight:700; text-transform:uppercase;
             letter-spacing:0.6px; margin-bottom:4px; }}
.gap-val  {{ font-size:20px; font-weight:800; letter-spacing:-0.3px; line-height:1; }}
.gap-pct  {{ display:inline-block; font-size:9px; font-weight:700;
             border-radius:4px; padding:2px 7px; margin-top:5px; }}
.gap-sub  {{ font-size:8.5px; color:#94A3B8; margin-top:3px; }}

/* amber gap */
.gap-amber {{ border-color:#FDE68A; }}
.gap-amber .gap-type {{ color:#92400E; }}
.gap-amber .gap-val  {{ color:#92400E; }}
.gap-amber .gap-pct  {{ background:#FFFBEB; color:#92400E; border:1px solid #FDE68A; }}

/* red gap */
.gap-red {{ border-color:#FECACA; }}
.gap-red .gap-type {{ color:#991B1B; }}
.gap-red .gap-val  {{ color:#991B1B; }}
.gap-red .gap-pct  {{ background:#FEF2F2; color:#991B1B; border:1px solid #FECACA; }}

/* ── kpi row ── */
.kpi-row {{ display:flex; gap:10px; }}
.kpi {{
  flex:1; background:white; border-radius:10px; border:1px solid #E2E8F0;
  border-top:4px solid; padding:14px 14px 12px;
  box-shadow:0 1px 3px rgba(0,0,0,0.04);
  opacity:0; transform:translateY(10px);
  transition:opacity 0.4s ease, transform 0.4s ease, box-shadow 0.15s;
}}
.kpi.show {{ opacity:1; transform:translateY(0); }}
.kpi.show:hover {{ box-shadow:0 5px 14px rgba(0,0,0,0.08); transform:translateY(-2px); }}
.b-navy   {{ border-top-color:#1E3A5F; }}
.b-teal   {{ border-top-color:#0F766E; }}
.b-indigo {{ border-top-color:#4338CA; }}
.b-amber  {{ border-top-color:#B45309; }}
.b-red    {{ border-top-color:#B91C1C; }}
.kpi-top  {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:4px; }}
.kpi-val  {{ font-size:21px; font-weight:800; color:#0F172A; letter-spacing:-0.4px; }}
.kpi-badge {{ font-size:9px; font-weight:700; border-radius:4px; padding:2px 7px; margin-top:3px; white-space:nowrap; }}
.bg-navy   {{ background:#EFF6FF; color:#1E3A5F; }}
.bg-teal   {{ background:#F0FDFA; color:#0F766E; }}
.bg-indigo {{ background:#EEF2FF; color:#4338CA; }}
.bg-amber  {{ background:#FFFBEB; color:#92400E; }}
.bg-red    {{ background:#FEF2F2; color:#991B1B; }}
.kpi-lbl  {{ font-size:10px; font-weight:700; color:#374151; text-transform:uppercase; letter-spacing:0.5px; }}
.kpi-sub  {{ font-size:9px; color:#9CA3AF; margin-top:2px; }}
</style>

<!-- HEADER -->
<div class="header">
  <div class="h-left">
    <div class="h-icon">🏥</div>
    <div>
      <div class="h-title">EHR–LIMS · Viral Load Validation</div>
      <div class="h-sub">Data capture &amp; leakage analysis across activated facilities</div>
      <div class="h-tags">
        <span class="h-tag"><span class="live-dot"></span>Live · SharePoint</span>
        <span class="h-tag">{dff['District'].nunique()} districts</span>
        <span class="h-tag">{n_fac} facilities</span>
        <span class="h-tag">{len(sel_months)} months</span>
      </div>
    </div>
  </div>
  <div class="h-right">
    <div class="h-ts-lbl">Last updated</div>
    <div class="h-ts-val">{datetime.now().strftime('%d %b %Y · %H:%M')}</div>
  </div>
</div>

<!-- ANIMATED FLOW TREE -->
<div class="stage">
  <button class="replay-btn" onclick="runAnimation()">↺ Replay</button>

  <div class="flow-row">

    <!-- PAPER NODE -->
    <div class="node n-paper" id="nd-paper">
      <div class="node-icon">📋</div>
      <div class="node-val" id="v-paper">0</div>
      <div class="node-lbl">Paper Samples</div>
      <div class="node-sub">Total VL collected</div>
    </div>

    <!-- CONNECTOR 1 -->
    <div class="connector">
      <div class="arrow-track" id="arr1"></div>
      <div class="drop-wrap" id="drop1">
        <div class="drop-line gap-amber" id="dl1"
             style="--dc:#F59E0B; height:44px;"></div>
        <div class="gap-card gap-amber" id="gc1">
          <div class="gap-type">Gap 1 — Paper vs EHR</div>
          <div class="gap-val" id="v-gap1">0</div>
          <div class="gap-pct">{gap1_pct}% Loss</div>
          <div class="gap-sub">Not recorded in EHR</div>
        </div>
      </div>
    </div>

    <!-- EHR NODE -->
    <div class="node n-ehr" id="nd-ehr">
      <div class="node-icon">💻</div>
      <div class="node-val" id="v-ehr">0</div>
      <div class="node-lbl">Captured in EHR</div>
      <div class="node-sub">Orders captured</div>
    </div>

    <!-- CONNECTOR 2 -->
    <div class="connector">
      <div class="arrow-track" id="arr2"></div>
      <div class="drop-wrap" id="drop2">
        <div class="drop-line gap-red" id="dl2"
             style="--dc:#EF4444; height:44px;"></div>
        <div class="gap-card gap-red" id="gc2">
          <div class="gap-type">Gap 2 — EHR vs SHR</div>
          <div class="gap-val" id="v-gap2">0</div>
          <div class="gap-pct">{gap2_pct}% Loss</div>
          <div class="gap-sub">Not submitted to SHR</div>
        </div>
      </div>
    </div>

    <!-- SHR NODE -->
    <div class="node n-shr" id="nd-shr">
      <div class="node-icon">🏛️</div>
      <div class="node-val" id="v-shr">0</div>
      <div class="node-lbl">Submitted to SHR</div>
      <div class="node-sub">Samples submitted</div>
    </div>

  </div>
</div>

<!-- KPI CARDS -->
<div class="kpi-row">
  <div class="kpi b-navy" id="kc1">
    <div class="kpi-top"><div class="kpi-val" id="k1">0</div><span class="kpi-badge bg-navy">{n_fac} sites</span></div>
    <div class="kpi-lbl">Total Paper Samples</div><div class="kpi-sub">VL samples collected</div>
  </div>
  <div class="kpi b-teal" id="kc2">
    <div class="kpi-top"><div class="kpi-val" id="k2">0</div><span class="kpi-badge bg-teal">{capture_rate}%</span></div>
    <div class="kpi-lbl">Captured in EHR</div><div class="kpi-sub">Capture Rate</div>
  </div>
  <div class="kpi b-indigo" id="kc3">
    <div class="kpi-top"><div class="kpi-val" id="k3">0</div><span class="kpi-badge bg-indigo">{submit_rate}%</span></div>
    <div class="kpi-lbl">Submitted to SHR</div><div class="kpi-sub">Submission Rate</div>
  </div>
  <div class="kpi b-amber" id="kc4">
    <div class="kpi-top"><div class="kpi-val" id="k4">0</div><span class="kpi-badge bg-amber">{gap1_pct}% Loss</span></div>
    <div class="kpi-lbl">Gap 1 — Paper vs EHR</div><div class="kpi-sub">Not recorded in EHR</div>
  </div>
  <div class="kpi b-red" id="kc5">
    <div class="kpi-top"><div class="kpi-val" id="k5">0</div><span class="kpi-badge bg-red">{gap2_pct}% Loss</span></div>
    <div class="kpi-lbl">Gap 2 — EHR vs SHR</div><div class="kpi-sub">Not submitted to SHR</div>
  </div>
</div>

<script>
var DATA = {{
  paper:{int(total_paper)}, ehr:{int(total_ehr)}, shr:{int(total_shr)},
  gap1:{int(gap1_tot)},     gap2:{int(gap2_tot)}
}};

function countUp(id, target, dur, delay) {{
  setTimeout(function() {{
    var el = document.getElementById(id);
    if (!el) return;
    var t0 = performance.now();
    (function tick(now) {{
      var p = Math.min((now-t0)/dur,1), e = 1-Math.pow(1-p,3);
      el.textContent = Math.floor(e*target).toLocaleString();
      if(p<1) requestAnimationFrame(tick);
      else el.textContent = target.toLocaleString();
    }})(performance.now());
  }}, delay);
}}

function show(id, delay, extra) {{
  setTimeout(function() {{
    var el = document.getElementById(id);
    if(el) {{ el.classList.add('show'); if(extra) extra(el); }}
  }}, delay);
}}

function resetAll() {{
  ['nd-paper','nd-ehr','nd-shr','arr1','arr2',
   'drop1','drop2','dl1','dl2','gc1','gc2',
   'kc1','kc2','kc3','kc4','kc5'].forEach(function(id) {{
    var el = document.getElementById(id);
    if(el) el.classList.remove('show');
  }});
  ['v-paper','v-ehr','v-shr','v-gap1','v-gap2',
   'k1','k2','k3','k4','k5'].forEach(function(id) {{
    var el = document.getElementById(id);
    if(el) el.textContent = '0';
  }});
}}

function runAnimation() {{
  resetAll();

  // 1. Paper node slides up
  show('nd-paper', 300);
  countUp('v-paper', DATA.paper, 900, 400);

  // 2. Arrow 1 draws right
  show('arr1', 1400);

  // 3. Gap 1 branch drops
  show('drop1', 1900);
  show('dl1', 2000);
  show('gc1', 2500);
  countUp('v-gap1', DATA.gap1, 600, 2550);

  // 4. EHR node slides up
  show('nd-ehr', 2200);
  countUp('v-ehr', DATA.ehr, 900, 2300);

  // 5. Arrow 2 draws right
  show('arr2', 3300);

  // 6. Gap 2 branch drops (bigger)
  show('drop2', 3800);
  show('dl2', 3900);
  show('gc2', 4400);
  countUp('v-gap2', DATA.gap2, 700, 4450);

  // 7. SHR node slides up
  show('nd-shr', 4100);
  countUp('v-shr', DATA.shr, 900, 4200);

  // 8. KPI cards
  show('kc1', 5200); countUp('k1', DATA.paper, 700, 5250);
  show('kc2', 5400); countUp('k2', DATA.ehr,   700, 5450);
  show('kc3', 5600); countUp('k3', DATA.shr,   700, 5650);
  show('kc4', 5800); countUp('k4', DATA.gap1,  600, 5850);
  show('kc5', 6000); countUp('k5', DATA.gap2,  600, 6050);
}}

window.addEventListener('load', function() {{
  setTimeout(runAnimation, 500);
}});
</script>
""", height=560)
# ─────────────────────────────────────────────────────────────────────────────
# FACILITY AGGREGATES
# ─────────────────────────────────────────────────────────────────────────────
fac = dff.groupby(['District','Facility'], as_index=False).agg(
    Paper=('VL Paper (BAs)','sum'), EHR=('VL EHR (BAs)','sum'), SHR=('VL SHR (Jima)','sum')
)
fac['Gap1']   = fac['Paper'] - fac['EHR']
fac['Gap2']   = fac['EHR']   - fac['SHR']
fac['Gap1 %'] = (fac['Gap1']/fac['Paper']*100).round(1)
fac['Gap2 %'] = (fac['Gap2']/fac['EHR']*100).round(1)

# ─────────────────────────────────────────────────────────────────────────────
# GAP CHARTS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div style="font-size:14px;font-weight:600;color:#0D1B2A;margin:28px 0 12px;display:flex;align-items:center;gap:8px">📊 Data leakage by facility<span style="flex:1;height:1px;background:#E8EDF3;display:inline-block;margin-left:8px"></span></div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)

def styled_bar(df_in, bg_col, fg_col, bg_name, fg_name, gap_col, gap_pct_col, title, subtitle):
    s = df_in.sort_values(gap_col, ascending=False)
    colors = []
    for v in s[gap_pct_col]:
        if pd.isna(v):     colors.append('#94A3B8')
        elif v > 30:       colors.append('#EF4444')
        elif v > 10:       colors.append('#F59E0B')
        else:              colors.append('#10B981')

    fig = go.Figure()
    fig.add_bar(y=s['Facility'], x=s[bg_col], name=bg_name,
                orientation='h', marker_color='#E2E8F0',
                hovertemplate='<b>%{y}</b><br>'+bg_name+': %{x:,}<extra></extra>')
    fig.add_bar(y=s['Facility'], x=s[fg_col], name=fg_name,
                orientation='h', marker_color=colors,
                hovertemplate='<b>%{y}</b><br>'+fg_name+': %{x:,}<br>Gap: %{customdata:.1f}%<extra></extra>',
                customdata=s[gap_pct_col])
    fig.update_layout(
        title=dict(text=f'<b>{title}</b><br><span style="font-size:11px;color:#94A3B8">{subtitle}</span>',
                   font=dict(size=13), x=0),
        barmode='overlay', height=420,
        margin=dict(l=10,r=20,t=60,b=10),
        legend=dict(orientation='h', yanchor='bottom', y=1.08, font=dict(size=11)),
        xaxis=dict(title='Sample count', gridcolor='#F1F5F9', tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10)),
        plot_bgcolor='white', paper_bgcolor='white',
    )
    return fig

with col_a:
    st.plotly_chart(
        styled_bar(fac, 'Paper','EHR','Paper (BAs)','EHR Captured',
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
# MONTHLY TREND + CAPTURE RATE DONUT
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div style="font-size:14px;font-weight:600;color:#0D1B2A;margin:28px 0 12px;display:flex;align-items:center;gap:8px">📈 Monthly trend & capture rates<span style="flex:1;height:1px;background:#E8EDF3;display:inline-block;margin-left:8px"></span></div>', unsafe_allow_html=True)

col_trend, col_donut = st.columns([2.2, 1])

monthly = dff.groupby('Month', as_index=False).agg(
    Paper=('VL Paper (BAs)','sum'), EHR=('VL EHR (BAs)','sum'), SHR=('VL SHR (Jima)','sum')
)
monthly['Month Date'] = monthly['Month'].map(MONTH_DATES)
monthly = monthly.sort_values('Month Date')
monthly['Gap1'] = monthly['Paper'] - monthly['EHR']
monthly['Gap2'] = monthly['EHR']   - monthly['SHR']

with col_trend:
    fig_trend = go.Figure()
    # Fill area between Paper and EHR (gap 1)
    fig_trend.add_scatter(
        x=monthly['Month'], y=monthly['Paper'], name='Paper (BAs)',
        mode='lines+markers', line=dict(color='#3B82F6', width=2.5),
        marker=dict(size=8, color='white', line=dict(color='#3B82F6',width=2)),
        fill=None)
    fig_trend.add_scatter(
        x=monthly['Month'], y=monthly['EHR'], name='EHR (BAs)',
        mode='lines+markers', line=dict(color='#10B981', width=2.5),
        marker=dict(size=8, color='white', line=dict(color='#10B981',width=2)),
        fill='tonexty', fillcolor='rgba(59,130,246,0.07)')
    fig_trend.add_scatter(
        x=monthly['Month'], y=monthly['SHR'], name='SHR (Jima)',
        mode='lines+markers', line=dict(color='#8B5CF6', width=2.5),
        marker=dict(size=8, color='white', line=dict(color='#8B5CF6',width=2)),
        fill='tonexty', fillcolor='rgba(16,185,129,0.07)')
    fig_trend.update_layout(
        height=300, margin=dict(l=10,r=10,t=20,b=10),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, font=dict(size=11)),
        xaxis=dict(gridcolor='#F1F5F9'), yaxis=dict(gridcolor='#F1F5F9', title='Samples'),
        plot_bgcolor='white', paper_bgcolor='white',
        hovermode='x unified',
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col_donut:
    # Funnel/donut showing overall pipeline retention
    fig_donut = go.Figure(go.Funnel(
        y=['Paper collected','Captured in EHR','Submitted to SHR'],
        x=[int(total_paper), int(total_ehr), int(total_shr)],
        textinfo='value+percent initial',
        marker=dict(color=['#3B82F6','#10B981','#8B5CF6'],
                    line=dict(color='white', width=2)),
        connector=dict(line=dict(color='#F1F5F9', width=1)),
        textfont=dict(size=11),
    ))
    fig_donut.update_layout(
        title=dict(text='<b>Pipeline retention</b>', font=dict(size=13), x=0.02),
        height=300, margin=dict(l=10,r=10,t=50,b=10),
        paper_bgcolor='white', plot_bgcolor='white',
        showlegend=False,
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# LEADERBOARD + DRILLDOWN
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-hdr">🏆 Leakage leaderboard & facility drilldown</div>',
            unsafe_allow_html=True)

col_lb, col_drill = st.columns([1.3, 1])

with col_lb:
    board = fac.sort_values('Gap1 %', ascending=False).reset_index(drop=True)

    def badge(pct):
        if pd.isna(pct):  return f'<span class="lb-badge badge-purple">N/A</span>'
        if pct > 30:      return f'<span class="lb-badge badge-red">{pct:.1f}%</span>'
        if pct > 10:      return f'<span class="lb-badge badge-amber">{pct:.1f}%</span>'
        return                   f'<span class="lb-badge badge-green">{pct:.1f}%</span>'

    def mini_bar(ehr, paper, color):
        pct = min(ehr/paper*100, 100) if paper > 0 else 0
        return f"""<div style="background:#F1F5F9;border-radius:4px;height:6px;width:100%">
            <div style="background:{color};height:6px;border-radius:4px;width:{pct:.0f}%"></div>
        </div>"""

    html_rows = ""
    for i, row in board.iterrows():
        critical = ' critical' if (not pd.isna(row['Gap1 %']) and row['Gap1 %'] > 30) else ''
        rank_icon = ['🥇','🥈','🥉'][i] if i < 3 else f'#{i+1}'
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

    components.html(f"""
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
    """, height=min(80 * len(board) + 20, 520), scrolling=True)

with col_drill:
    sel_fac = st.selectbox("Select facility", sorted(dff['Facility'].unique()),
                           label_visibility="collapsed")
    fac_df = dff[dff['Facility'] == sel_fac].sort_values('Month Date')
    act = fac_df['Activation Date'].iloc[0] if not fac_df.empty else None
    dist = fac_df['District'].iloc[0] if not fac_df.empty else '—'
    g1   = fac_df['Gap1'].sum()
    g2   = fac_df['Gap2'].sum()
    g1p  = fac_df['Gap1 %'].mean()
    g2p  = fac_df['Gap2 %'].mean()

    # Mini stat row
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown(f"""<div class="drill-stat">
            <div class="ds-lbl">District</div>
            <div class="ds-val" style="font-size:15px">{dist}</div>
        </div>
        <div class="drill-stat">
            <div class="ds-lbl">Gap 1 total</div>
            <div class="ds-val" style="color:#F59E0B">{int(g1):,} <span style="font-size:12px">({g1p:.1f}%)</span></div>
        </div>""", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""<div class="drill-stat">
            <div class="ds-lbl">Activated</div>
            <div class="ds-val" style="font-size:15px">{act.strftime('%b %Y') if act else '—'}</div>
        </div>
        <div class="drill-stat">
            <div class="ds-lbl">Gap 2 total</div>
            <div class="ds-val" style="color:#EF4444">{int(g2):,} <span style="font-size:12px">({g2p:.1f}%)</span></div>
        </div>""", unsafe_allow_html=True)

    fig_drill = go.Figure()
    fig_drill.add_scatter(x=fac_df['Month'], y=fac_df['VL Paper (BAs)'], name='Paper',
        mode='lines+markers', line=dict(color='#3B82F6',width=2.5),
        marker=dict(size=9,color='white',line=dict(color='#3B82F6',width=2)))
    fig_drill.add_scatter(x=fac_df['Month'], y=fac_df['VL EHR (BAs)'],   name='EHR',
        mode='lines+markers', line=dict(color='#10B981',width=2.5),
        marker=dict(size=9,color='white',line=dict(color='#10B981',width=2)))
    fig_drill.add_scatter(x=fac_df['Month'], y=fac_df['VL SHR (Jima)'],  name='SHR',
        mode='lines+markers', line=dict(color='#8B5CF6',width=2.5),
        marker=dict(size=9,color='white',line=dict(color='#8B5CF6',width=2)))
    fig_drill.update_layout(
        height=220, margin=dict(l=10,r=10,t=10,b=10),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,font=dict(size=10)),
        xaxis=dict(gridcolor='#F1F5F9',tickfont=dict(size=9)),
        yaxis=dict(gridcolor='#F1F5F9',tickfont=dict(size=9)),
        plot_bgcolor='white', paper_bgcolor='white', hovermode='x unified',
    )
    st.plotly_chart(fig_drill, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""<div style="text-align:center;margin-top:32px;padding:16px;
    color:#94A3B8;font-size:11px;border-top:1px solid #E8EDF3;">
    🔴 >30% gap · 🟡 10–30% · 🟢 &lt;10% &nbsp;|&nbsp;
    Analysis starts the month <i>after</i> facility go-live &nbsp;|&nbsp;
    Zim-TTECH · EHR–LIMS Validation
</div>""", unsafe_allow_html=True)
