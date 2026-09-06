import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date, timedelta
from io import BytesIO


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="HealthCare Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="auto"
)


# =========================================================
# HTML RENDER HELPER
# -----------------------------------------------------------
# Streamlit's Markdown parser treats any line indented 4+
# spaces as a code block (before HTML is even considered), so
# hand-indented f-strings print as literal text instead of
# rendering. This strips leading whitespace per line, and
# every "card" is built as ONE string / ONE st.markdown call
# so open/close <div> tags actually wrap their content.
# =========================================================

def render(html: str):
    lines = html.strip("\n").split("\n")
    st.markdown("\n".join(line.strip() for line in lines), unsafe_allow_html=True)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    .stApp { background-color: #eef2f7; }
    .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1500px; }

    #MainMenu { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; box-shadow: none; }

    /* ---------- SIDEBAR ---------- */

    [data-testid="stSidebar"] {
        background-color: #0f172a;
        min-width: 230px !important;
        max-width: 250px !important;
        border-radius: 0 24px 24px 0;
    }

    

    [data-testid="stSidebar"] * { color: #cbd5e1; }

    .sb-logo { font-size: 24px; font-weight: 800; color: #ffffff !important; margin-bottom: 2px; }
    .sb-subtitle { font-size: 12px; opacity: 0.6; margin-bottom: 18px; }
    .sb-section {
        font-size: 11px; text-transform: uppercase; letter-spacing: 1px;
        opacity: 0.55; margin-top: 20px; margin-bottom: 8px;
    }

    [data-testid="stSidebar"] .stButton > button {
    width: 100%;
    text-align: left;
    background: transparent;
    border: 1px solid transparent;
    color: #cbd5e1;
    font-weight: 500;
    font-size: 14px;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 4px;
    box-shadow: none;
    transition: all 0.2s ease;
}

/* Hover */
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(20, 184, 166, 0.12) !important;
    border-color: rgba(20, 184, 166, 0.25) !important;
    color: #ffffff !important;
    transform: translateX(3px);
}

/* Active page */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #14b8a6, #2563eb) !important;
    border-color: transparent !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(20, 184, 166, 0.30);
    transform: translateX(0);
}

/* Active page should not move on hover */
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #0f766e, #1d4ed8) !important;
    transform: translateX(0);
}

    /* Filter widgets */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.14) !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background-color: rgba(20,184,166,0.22) !important;
        border: 1px solid #14b8a6 !important;
        border-radius: 8px !important;
        color: #ecfeff !important;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] svg { fill: #ecfeff !important; }
    [data-testid="stSidebar"] .stMultiSelect label {
        font-size: 12.5px !important; font-weight: 600 !important; color: #e2e8f0 !important; margin-bottom: 2px !important;
    }
    [data-testid="stSidebar"] .stMultiSelect { margin-bottom: 14px !important; }
    [data-testid="stSidebar"] .stSlider label, [data-testid="stSidebar"] .stDateInput label {
        font-size: 12.5px !important; font-weight: 600 !important; color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        border: 1px solid rgba(255,255,255,0.12); border-radius: 10px; margin-top: 8px;
    }

    /* ---------- TOP NAVBAR ---------- */

    .navbar-avatar {
        width: 58px; height: 55px; border-radius: 50%;
        background: linear-gradient(135deg, #14b8a6, #2563eb);
        color: white; display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 14px;
        flex-shrink: 0;
        white-space: nowrap;
    }

    /* ---------- HERO CARD ---------- */

    .hero-card {
        background: linear-gradient(135deg, #0f766e 0%, #0891b2 55%, #2563eb 100%);
        padding: 26px 30px; border-radius: 20px; color: white; width: 100%;
        box-shadow: 0 8px 20px rgba(15, 118, 110, 0.25);
    }
    .hero-title { font-size: 24px; font-weight: 800; margin-bottom: 4px; }
    .hero-text { font-size: 13.5px; opacity: 0.92; }

    /* ---------- KPI CARDS ---------- */

    .metric-card {
        background-color: white;
        border-radius: 16px;
        padding: 18px 20px;
        min-height: 90px;
        height: 100%;
        border: 1px solid #e2e8f0;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.05);

        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: flex-start;
        gap: 14px;

        box-sizing: border-box;
        overflow: visible;
        position: relative;
    }

    /* Stacked variant: icon on top, then label/value/sub below.
       Used by the billing-style KPI cards (4 flat sibling divs),
       as opposed to .metric-card's icon-beside-text row layout. */
    .metric-card-stacked {
        background-color: white;
        border-radius: 16px;
        padding: 18px 20px;
        min-height: 110px;
        height: 100%;
        border: 1px solid #e2e8f0;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.05);

        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-content: center;

        box-sizing: border-box;
        overflow: visible;
        position: relative;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card-stacked:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 22px rgba(15, 23, 42, 0.10);
    }
    .metric-card-stacked:hover .metric-sub {
        display: block;
        position: absolute;
        left: calc(50% + 2px);
        top: 50%;
        transform: translateY(-50%);
        background: #0f172a;
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 12px;
        line-height: 1.4;
        white-space: nowrap;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
        z-index: 5;
    }

    .metric-sub {
        display: none;
    }

    .metric-card:hover .metric-sub {
        display: block;
        position: absolute;
        left: calc(50% + 2px);
        top: 50%;
        transform: translateY(-50%);
        background: #0f172a;
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 12px;
        line-height: 1.4;
        white-space: nowrap;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
        z-index: 5;
    }
    .metric-badge {
        width: 46px; height: 46px; border-radius: 12px; display: flex;
        align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0;
    }
    .badge-blue { background: #dbeafe; }
    .badge-red { background: #fee2e2; }
    .badge-teal { background: #ccfbf1; }
    .badge-purple { background: #ede9fe; }
    .metric-label { color: #64748b; font-size: 12.5px; margin-bottom: 2px; }
    .metric-value { color: #0f172a; font-size: 22px; font-weight: 800; }
    .trend-up { color: #16a34a; font-size: 11px; font-weight: 700; margin-top: 3px; }
    .trend-down { color: #dc2626; font-size: 11px; font-weight: 700; margin-top: 3px; }

    /* ---------- SECTION TITLES ---------- */

    .section-title { font-size: 18px; font-weight: 800; color: #0f172a; margin-top: 26px; margin-bottom: 12px; }
    .section-subtitle { color: #64748b; font-size: 12.5px; margin-top: -8px; margin-bottom: 12px; }

    /* ---------- CARDS + HOVER ---------- */

    .chart-card, .panel-card {
        background-color: white; border-radius: 16px; border: 1px solid #e2e8f0;
        padding: 18px; box-shadow: 0 3px 12px rgba(15, 23, 42, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card { transition: transform 0.15s ease, box-shadow 0.15s ease; }
    .chart-card:hover, .panel-card:hover, .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 22px rgba(15, 23, 42, 0.10);
    }
    .panel-title { font-weight: 700; font-size: 14.5px; color: #0f172a; margin-bottom: 12px; }
    .empty-state { color: #94a3b8; font-size: 13px; padding: 14px 4px; text-align: center; }

    /* ---------- CALENDAR STRIP (real buttons, styled) ---------- */

    .st-key-cal_strip .stButton > button {
        border-radius: 10px !important;
        padding: 10px 0 !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        background: #f8fafc !important;
        color: #0f172a !important;
        border: 1px solid #eef2f7 !important;
    }
    .st-key-cal_strip .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #14b8a6, #2563eb) !important;
        color: #ffffff !important;
        border: none !important;
    }
    .cal-dow-label { text-align: center; font-size: 10px; color: #64748b; margin-bottom: 3px; }

    /* ---------- LIST ROW ---------- */

    .list-row { display: flex; align-items: center; gap: 12px; padding: 10px 8px; border-radius: 10px; margin-bottom: 6px; background: #f8fafc; }
    .list-avatar {
        width: 34px; height: 34px; border-radius: 50%; background: #e0f2fe;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; color: #0369a1; font-size: 12px; flex-shrink: 0;
    }
    .list-name { font-size: 13px; font-weight: 700; color: #0f172a; }
    .list-sub { font-size: 11.5px; color: #64748b; }

    /* ---------- BADGES ---------- */

    .badge { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 700; }
    .badge-green { background: #dcfce7; color: #16a34a; }
    .badge-blue2 { background: #dbeafe; color: #2563eb; }
    .badge-amber { background: #fef3c7; color: #d97706; }
    .badge-red2 { background: #fee2e2; color: #dc2626; }
    .badge-gray { background: #f1f5f9; color: #475569; }

    /* ---------- TABLE ---------- */

    table.simple-table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
    table.simple-table th {
        text-align: left; color: #94a3b8; font-weight: 600; font-size: 11px;
        text-transform: uppercase; letter-spacing: 0.4px; padding: 6px 8px; border-bottom: 1px solid #eef2f7;
    }
    table.simple-table td { padding: 9px 8px; border-bottom: 1px solid #f1f5f9; color: #0f172a; }

    hr { border: none; border-top: 1px solid #e2e8f0; margin: 22px 0; }

    .main .stButton > button {
    border-radius: 10px !important;
    border: none !important;
    background: linear-gradient(135deg, #14b8a6, #2563eb) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

.main .stButton > button:hover,
.main .stButton > button:focus,
.main .stButton > button:active {
    background: linear-gradient(135deg, #0f766e, #1d4ed8) !important;
    color: #ffffff !important;
    border: none !important;
}

.main .stDownloadButton > button {
    border-radius: 10px !important;
    border: none !important;
    background: linear-gradient(135deg, #14b8a6, #2563eb) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

.main .stDownloadButton > button:hover,
.main .stDownloadButton > button:focus,
.main .stDownloadButton > button:active {
    background: linear-gradient(135deg, #0f766e, #1d4ed8) !important;
    color: #ffffff !important;
    border: none !important;
}

    /* ---------- MOBILE BREAKPOINT ---------- */

    @media (max-width: 900px) {
        [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
        [data-testid="stHorizontalBlock"] > div { flex: 1 1 100% !important; width: 100% !important; }
    }

    /* ================================
   CHART VISIBILITY FIX
   ================================ */

[data-testid="stMain"] .stMarkdown strong,
[data-testid="stMain"] .stMarkdown p {
    color: #0f172a !important;
}

.chart-title {
    color: #0f172a !important;
    font-size: 16px;
    font-weight: 800;
    margin-bottom: 14px;
}

/* Streamlit bordered containers - this is the ONE rule that
   makes st.container(border=True) look like our white cards.
   It applies to every bordered container anywhere in the main
   area, so any chart/table/panel wrapped this way is consistent. */
[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 18px !important;
    box-shadow: 0 3px 12px rgba(15, 23, 42, 0.05);
    margin-bottom: 18px;
}

.chart-title {
    color: #0f172a !important;
    font-size: 16px;
    font-weight: 800;
    margin-bottom: 14px;
}


/* =========================
   BILLING KPI COLORS
   ========================= */

.billing-total {
    border-left: 4px solid #0f766e;
}

.billing-average {
    border-left: 4px solid #2563eb;
}

.billing-highest {
    border-left: 4px solid #7c3aed;
}

.billing-lowest {
    border-left: 4px solid #f59e0b;
}

.billing-total .metric-icon {
    background: #ccfbf1;
    color: #0f766e;
}

.billing-average .metric-icon {
    background: #dbeafe;
    color: #2563eb;
}

.billing-highest .metric-icon {
    background: #ede9fe;
    color: #7c3aed;
}

.billing-lowest .metric-icon {
    background: #fef3c7;
    color: #d97706;
}

.metric-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    margin-bottom: 10px;
}

/* =========================
   BILLING INSIGHTS
   ========================= */

.insight-card {
    padding: 18px;
    border-radius: 12px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    height: 100%;
}

.insight-icon {
    font-size: 22px;
    margin-bottom: 8px;
}

.insight-title {
    font-size: 13px;
    font-weight: 600;
    color: #64748b;
    margin-bottom: 6px;
}

.insight-value {
    font-size: 20px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 6px;
}

.insight-text {
    font-size: 12px;
    color: #64748b;
    line-height: 1.5;
}

/* =========================
   PATIENT TABLE
   ========================= */

[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
}
/* =========================
   SIDEBAR NAVIGATION
   ========================= */

[data-testid="stSidebar"] button {
    border-radius: 10px;
    border: none;
    transition: all 0.2s ease;
}

[data-testid="stSidebar"] button:focus {
    outline: 2px solid rgba(20, 184, 166, 0.6);
    outline-offset: 1px;
}


/* =========================
   MOBILE RESPONSIVE
   ========================= */

@media (max-width: 768px) {

    .metric-card {
        min-height: 80px;
        padding: 16px;
    }

    .section-title {
        font-size: 20px;
    }

    .section-subtitle {
        font-size: 13px;
    }

    .chart-title {
        font-size: 16px;
    }
}

/* =========================================================
   BUTTON HOVER FIX
   ========================================================= */

[data-testid="stButton"] button:hover {
    background-color: #0f766e !important;
    color: white !important;
    border-color: #0f766e !important;
}

[data-testid="stButton"] button:hover p,
[data-testid="stButton"] button:hover span,
[data-testid="stButton"] button:hover div {
    color: white !important;
}


/* Download buttons */
[data-testid="stDownloadButton"] button:hover {
    background-color: #0f766e !important;
    color: white !important;
    border-color: #0f766e !important;
}

[data-testid="stDownloadButton"] button:hover p,
[data-testid="stDownloadButton"] button:hover span,
[data-testid="stDownloadButton"] button:hover div {
    color: white !important;
}
/* =========================================================
   MOBILE SIDEBAR FIX
   ========================================================= */

@media (max-width: 768px) {

    /* Let Streamlit control whether sidebar is open or closed */
    [data-testid="stSidebar"] {
        min-width: 0 !important;
        max-width: 85vw !important;
        width: 85vw !important;
        border-radius: 0 22px 22px 0;
    }

    /* Make sidebar content fit smaller screens */
    [data-testid="stSidebar"] .block-container {
        padding-left: 16px !important;
        padding-right: 16px !important;
    }

    /* Navigation buttons */
    [data-testid="stSidebar"] .stButton > button {
        font-size: 14px !important;
        padding: 10px 12px !important;
    }

    /* Main content */
    [data-testid="stMain"] .block-container {
        padding-left: 12px !important;
        padding-right: 12px !important;
    }

    /* KPI cards */
    .metric-card,
    .metric-card-stacked {
        min-height: 90px !important;
        padding: 14px !important;
    }

    /* Smaller hero */
    .hero-card {
        padding: 20px !important;
        border-radius: 16px !important;
    }

    .hero-title {
        font-size: 20px !important;
    }

    .hero-text {
        font-size: 12px !important;
    }

    /* Cards */
    .chart-card,
    .panel-card {
        padding: 12px !important;
        border-radius: 14px !important;
    }

    /* Tables can scroll horizontally */
    table.simple-table {
        min-width: 500px;
    }

    .panel-card {
        overflow-x: auto !important;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD DATA (cached, so filters/nav don't re-read the file)
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "cleaned" / "cleaned_healthcare_dataset.xlsx"


@st.cache_data(show_spinner="Loading patient data...")
def load_data(path):
    data = pd.read_excel(path)
    for col in ["Date of Admission", "Discharge Date"]:
        if col in data.columns:
            data[col] = pd.to_datetime(data[col], errors="coerce")
    return data


df = load_data(DATA_PATH)

REQUIRED_COLUMNS = [
    "Patient ID", "Name", "Age", "Gender", "Medical Condition",
    "Admission Type", "Billing Amount", "Test Results", "Medication",
]
missing_required = [c for c in REQUIRED_COLUMNS if c not in df.columns]
if missing_required:
    st.error(
        "Your dataset is missing required column(s): "
        + ", ".join(missing_required)
        + ". Please check cleaned_healthcare_dataset.xlsx."
    )
    st.stop()

HAS_DOCTOR = "Doctor" in df.columns
HAS_DATE = "Date of Admission" in df.columns and df["Date of Admission"].notna().any()
HAS_DISCHARGE = "Discharge Date" in df.columns
HAS_HOSPITAL = "Hospital" in df.columns
HAS_INSURANCE = "Insurance Provider" in df.columns
HAS_ROOM = "Room Number" in df.columns
HAS_BLOOD = "Blood Type" in df.columns


def badge_for_test_result(value):
    return {"Normal": "badge-green", "Abnormal": "badge-red2", "Inconclusive": "badge-amber"}.get(value, "badge-gray")


def badge_for_admission(value):
    return {"Emergency": "badge-red2", "Urgent": "badge-amber", "Elective": "badge-blue2"}.get(value, "badge-gray")


def initials(name):
    parts = str(name).split()
    return "".join(p[0] for p in parts[:2]).upper() if parts else "?"


def trend_html(pct):
    if pct is None:
        return ""
    arrow = "▲" if pct >= 0 else "▼"
    cls = "trend-up" if pct >= 0 else "trend-down"
    return f'<div class="{cls}">{arrow} {abs(pct):.1f}% vs earlier period</div>'


def compute_trend(data, column=None):
    """Compares the first half vs second half of the date-ordered data.
    column=None compares patient counts; otherwise compares the column's mean."""
    if not HAS_DATE:
        return None
    d = data.dropna(subset=["Date of Admission"]).sort_values("Date of Admission")
    if len(d) < 10:
        return None
    mid = len(d) // 2
    first, second = d.iloc[:mid], d.iloc[mid:]
    if column is None:
        v1, v2 = len(first), len(second)
    else:
        v1, v2 = first[column].mean(), second[column].mean()
    if not v1:
        return None
    return (v2 - v1) / v1 * 100


# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "selected_day" not in st.session_state:
    st.session_state.selected_day = None
if "patients_page" not in st.session_state:
    st.session_state.patients_page = 1

NAV_ITEMS = [
    ("📊", "Dashboard"),
    ("👥", "Patients"),
    ("🩺", "Medical Analysis"),
    ("💰", "Billing"),
    ("📈", "Reports"),
]


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    render('<div class="sb-logo">🏥 HealthCare</div>')
    render('<div class="sb-subtitle">Patient Analytics Platform</div>')

    for icon, label in NAV_ITEMS:
        is_active = st.session_state.page == label
        if st.button(f"{icon}   {label}", key=f"nav_{label}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.page = label
            st.rerun()

    render('<div class="sb-section">Filters</div>')

    selected_gender = st.multiselect(
        "🧑 Gender", options=sorted(df["Gender"].unique()),
        default=sorted(df["Gender"].unique()), key="filter_gender"
    )
    selected_condition = st.multiselect(
        "🩺 Medical Condition", options=sorted(df["Medical Condition"].unique()),
        default=sorted(df["Medical Condition"].unique()), key="filter_condition"
    )
    selected_admission = st.multiselect(
        "🏨 Admission Type", options=sorted(df["Admission Type"].unique()),
        default=sorted(df["Admission Type"].unique()), key="filter_admission"
    )

    bill_min, bill_max = float(df["Billing Amount"].min()), float(df["Billing Amount"].max())
    with st.expander("⚙️ Advanced filters"):
        billing_range = st.slider(
            "Billing amount ($)", min_value=bill_min, max_value=bill_max,
            value=(bill_min, bill_max), key="filter_billing"
        )
        date_range = None
        if HAS_DATE:
            valid_dates = df["Date of Admission"].dropna()
            dmin, dmax = valid_dates.min().date(), valid_dates.max().date()
            date_range = st.date_input(
                "Admission date range", value=(dmin, dmax),
                min_value=dmin, max_value=dmax, key="filter_daterange"
            )

    if st.button("↺  Reset filters", use_container_width=True, key="reset_filters"):
        for k in ["filter_gender", "filter_condition", "filter_admission",
                   "filter_billing", "filter_daterange", "search_box",
                   "sort_by", "sort_dir", "page_size", "patient_lookup"]:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state.selected_day = None
        st.session_state.patients_page = 1
        st.rerun()


# =========================================================
# APPLY FILTERS
# =========================================================

mask = (
    df["Gender"].isin(selected_gender)
    & df["Medical Condition"].isin(selected_condition)
    & df["Admission Type"].isin(selected_admission)
    & df["Billing Amount"].between(billing_range[0], billing_range[1])
)

filtered_df = df[mask]

if HAS_DATE and date_range and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[filtered_df["Date of Admission"].between(start, end)]

if filtered_df.empty:
    st.warning("No patients match the current filters. Adjust the filters in the sidebar, or hit **Reset filters**.")
    st.stop()


# =========================================================
# TOP NAVBAR
# =========================================================

nav_l, nav_r = st.columns([3, 1])

with nav_l:
    search_term = st.text_input(
        "search", placeholder="🔍  Search patients, doctors, conditions...",
        label_visibility="collapsed", key="search_box"
    )

with nav_r:
    render("""
    <div style="display:flex; align-items:center; justify-content:flex-end; gap:10px; height:38px;">
        <div style="font-size:18px;">🔔</div>
        <div style="font-size:18px;">⚙️</div>
        <div class="navbar-avatar">Kay Que</div>
    </div>
    """)

if search_term:
    smask = filtered_df["Name"].astype(str).str.contains(search_term, case=False, na=False)
    smask |= filtered_df["Medical Condition"].astype(str).str.contains(search_term, case=False, na=False)
    if HAS_DOCTOR:
        smask |= filtered_df["Doctor"].astype(str).str.contains(search_term, case=False, na=False)
    filtered_df = filtered_df[smask]

if filtered_df.empty:
    st.info(f"No results for '{search_term}'. Try a different search term.")
    st.stop()


# =========================================================
# HERO CARD
# =========================================================

hero_l, hero_r = st.columns([3, 1.4])

with hero_l:
    render(f"""
    <div class="hero-card">
        <div class="hero-title">Good Morning 👋</div>
        <div class="hero-text">
            You're viewing <b>{st.session_state.page}</b> — {len(filtered_df):,} patients match your current filters.
        </div>
    </div>
    """)

with hero_r:
    st.write("")
    b1, b2 = st.columns(2)
    with b1:
        st.button("＋ Add Patient", use_container_width=True)
    with b2:
        st.button("＋ New Report", use_container_width=True)


# =========================================================
# KPI ROW
# =========================================================

render('<div class="section-title">Overview</div>')

col1, col2, col3, col4 = st.columns(4)

with col1:
    count_trend = compute_trend(filtered_df, None)
    render(f"""
    <div class="metric-card">
        <div class="metric-badge badge-blue">👥</div>
        <div>
            <div class="metric-label">Total Patients</div>
            <div class="metric-value">{len(filtered_df):,}</div>
            {trend_html(count_trend)}
        </div>
    </div>
    """)

with col2:
    avg_age = filtered_df["Age"].mean()
    age_trend = compute_trend(filtered_df, "Age")
    render(f"""
    <div class="metric-card">
        <div class="metric-badge badge-red">🎂</div>
        <div>
            <div class="metric-label">Average Age</div>
            <div class="metric-value">{avg_age:.1f} yrs</div>
            {trend_html(age_trend)}
        </div>
    </div>
    """)

with col3:
    avg_bill = filtered_df["Billing Amount"].mean()
    bill_trend = compute_trend(filtered_df, "Billing Amount")
    render(f"""
    <div class="metric-card">
        <div class="metric-badge badge-teal">💰</div>
        <div>
            <div class="metric-label">Average Billing</div>
            <div class="metric-value">${avg_bill:,.0f}</div>
            {trend_html(bill_trend)}
        </div>
    </div>
    """)

with col4:
    conditions = filtered_df["Medical Condition"].nunique()
    render(f"""
    <div class="metric-card">
        <div class="metric-badge badge-purple">🩺</div>
        <div>
            <div class="metric-label">Medical Conditions</div>
            <div class="metric-value">{conditions}</div>
        </div>
    </div>
    """)

if not HAS_DATE:
    st.caption("Add a 'Date of Admission' column to unlock trend indicators and a real activity calendar.")


# =========================================================
# SECTION BUILDERS
# =========================================================

def section_patient_activity(data):
    render('<div class="section-title">Patient Activity</div>')
    left, right = st.columns([1.1, 1.6])

    # Determine the 7 days shown in the strip: the most recent
    # 7 distinct admission dates if we have real dates, otherwise
    # fall back to the current calendar week (non-interactive).
    week_dates, clickable = [], False
    if HAS_DATE:
        valid_dates = data["Date of Admission"].dropna()
        if not valid_dates.empty:
            week_dates = sorted(valid_dates.dt.date.unique())[-7:]
            clickable = True
    if not week_dates:
        today = date.today()
        week_dates = [today - timedelta(days=today.weekday()) + timedelta(days=i) for i in range(7)]

    if clickable and st.session_state.selected_day in week_dates:
        day_data = data[data["Date of Admission"].dt.date == st.session_state.selected_day]
        subtitle = f"Admitted {st.session_state.selected_day.strftime('%b %d, %Y')}"
    else:
        day_data = data.sort_values("Date of Admission", ascending=False) if HAS_DATE else data
        subtitle = "Most recent patients"

    with left:
        with st.container(border=True):
            render('<div class="panel-title">📅 This Week</div>' if not clickable else '<div class="panel-title">📅 Recent Admission Dates</div>')

            with st.container(key="cal_strip"):
                cols = st.columns(7)
                for i, d in enumerate(week_dates):
                    with cols[i]:
                        render(f'<div class="cal-dow-label">{d.strftime("%a")}</div>')
                        is_active = clickable and st.session_state.selected_day == d
                        if st.button(str(d.day), key=f"day_{d.isoformat()}", use_container_width=True,
                                     type="primary" if is_active else "secondary", disabled=not clickable):
                            st.session_state.selected_day = None if is_active else d
                            st.rerun()

            render(f'<div class="panel-title">{subtitle}</div>')

            if day_data.empty:
                render('<div class="empty-state">No patients on this date.</div>')
            else:
                for _, row in day_data.head(5).iterrows():
                    doctor_txt = f" • Dr. {row['Doctor']}" if HAS_DOCTOR and pd.notna(row.get("Doctor")) else ""
                    render(f"""
                    <div class="list-row">
                        <div class="list-avatar">{initials(row['Name'])}</div>
                        <div><div class="list-name">{row['Name']}</div><div class="list-sub">{row['Medical Condition']}{doctor_txt}</div></div>
                    </div>
                    """)

    with right:
        rows = ""
        for _, row in day_data.head(8).iterrows():
            test_badge = badge_for_test_result(row.get("Test Results"))
            admit_badge = badge_for_admission(row.get("Admission Type"))
            rows += f"""
            <tr>
                <td>{row['Name']}</td>
                <td>{row['Medical Condition']}</td>
                <td><span class="badge {admit_badge}">{row['Admission Type']}</span></td>
                <td><span class="badge {test_badge}">{row['Test Results']}</span></td>
            </tr>
            """
        body = f'<table class="simple-table"><tr><th>Patient</th><th>Condition</th><th>Admission</th><th>Result</th></tr>{rows}</table>' \
            if not day_data.empty else '<div class="empty-state">No records to show.</div>'
        render(f"""
        <div class="panel-card">
            <div class="panel-title">🩺 Treatment Overview</div>
            {body}
        </div>
        """)


def section_medication_and_doctors(data):
    col1, col2 = st.columns(2)

    with col1:
        med_counts = data["Medication"].value_counts().head(6)
        if med_counts.empty:
            body = '<div class="empty-state">No medication data.</div>'
        else:
            rows = "".join(
                f'<tr><td>{med}</td><td>{count} patients</td><td><span class="badge badge-green">Active</span></td></tr>'
                for med, count in med_counts.items()
            )
            body = f'<table class="simple-table"><tr><th>Medication</th><th>Prescribed To</th><th>Status</th></tr>{rows}</table>'
        render(f'<div class="panel-card"><div class="panel-title">💊 Medication Overview</div>{body}</div>')

    with col2:
        if HAS_DOCTOR:
            doc_summary = (
                data.groupby("Doctor")
                .agg(Patients=("Patient ID", "count"),
                     Condition=("Medical Condition", lambda s: s.mode()[0] if not s.mode().empty else "-"))
                .sort_values("Patients", ascending=False)
                .head(6)
                .reset_index()
            )
            if doc_summary.empty:
                body = '<div class="empty-state">No doctor data.</div>'
            else:
                rows = "".join(
                    f'<tr><td>Dr. {r["Doctor"]}</td><td>{r["Condition"]}</td><td>{r["Patients"]} patients</td>'
                    f'<td><span class="badge badge-green">Available</span></td></tr>'
                    for _, r in doc_summary.iterrows()
                )
                body = f'<table class="simple-table"><tr><th>Doctor</th><th>Specialty</th><th>Caseload</th><th>Status</th></tr>{rows}</table>'
        else:
            body = '<div class="empty-state">Add a \'Doctor\' column to your dataset to populate this panel.</div>'
        render(f'<div class="panel-card"><div class="panel-title">👨‍⚕️ Top Doctors</div>{body}</div>')


def section_condition_charts(data):

    # -----------------------------
    # ROW 1
    # -----------------------------
    col1, col2 = st.columns(2)

    # Medical Condition
    with col1:
        with st.container(border=True):

            render("""
            <div class="chart-title">
                Patients by Medical Condition
            </div>
            """)

            condition_counts = (
                data["Medical Condition"]
                .value_counts()
                .reset_index()
            )

            condition_counts.columns = ["Condition", "Patients"]

            fig = px.bar(
                condition_counts,
                x="Condition",
                y="Patients"
            )

            fig.update_traces(
                marker_color="#0f766e",
                hovertemplate="<b>%{x}</b><br>Patients: %{y}<extra></extra>"
            )

            fig.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(
                    color="#0f172a",  # Dark, clear text color
                    size=12
                ),
                xaxis=dict(
                    title=None,
                    showgrid=False,
                    tickfont=dict(color="#0f172a", size=12) # Visible ticks
                ),
                yaxis=dict(
                    title=None,
                    gridcolor="#e2e8f0",
                    tickfont=dict(color="#0f172a", size=12) # Visible ticks
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )

    # Gender
    with col2:
        with st.container(border=True):

            render("""
            <div class="chart-title">
                Patients by Gender
            </div>
            """)

            gender_counts = (
                data["Gender"]
                .value_counts()
                .reset_index()
            )

            gender_counts.columns = ["Gender", "Patients"]

            fig = px.bar(
                gender_counts,
                x="Gender",
                y="Patients"
            )

            fig.update_traces(
                marker_color="#d97706",
                hovertemplate="<b>%{x}</b><br>Patients: %{y}<extra></extra>"
            )

            fig.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(
                    color="#0f172a",
                    size=12
                ),
                xaxis=dict(
                    title=None,
                    showgrid=False,
                    tickfont=dict(color="#0f172a", size=12)
                ),
                yaxis=dict(
                    title=None,
                    gridcolor="#e2e8f0",
                    tickfont=dict(color="#0f172a", size=12)
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )


    # -----------------------------
    # ROW 2
    # -----------------------------
    col1, col2 = st.columns(2)

    # Age Groups
    with col1:
        with st.container(border=True):

            render("""
            <div class="chart-title">
                Patients by Age Group
            </div>
            """)

            age_groups = pd.cut(
                data["Age"],
                bins=[17, 30, 45, 60, 75, 85],
                labels=[
                    "18–30",
                    "31–45",
                    "46–60",
                    "61–75",
                    "76–85"
                ]
            )

            age_counts = (
                age_groups
                .value_counts()
                .sort_index()
                .reset_index()
            )

            age_counts.columns = ["Age Group", "Patients"]

            fig = px.bar(
                age_counts,
                x="Age Group",
                y="Patients"
            )

            fig.update_traces(
                marker_color="#0f766e",
                hovertemplate="<b>%{x}</b><br>Patients: %{y}<extra></extra>"
            )

            fig.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(
                    color="#0f172a",
                    size=12
                ),
                xaxis=dict(
                    title=None,
                    showgrid=False,
                    tickfont=dict(color="#0f172a", size=12)
                ),
                yaxis=dict(
                    title=None,
                    gridcolor="#e2e8f0",
                    tickfont=dict(color="#0f172a", size=12)
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )

    # Test Results
    with col2:
        with st.container(border=True):

            render("""
            <div class="chart-title">
                Test Results
            </div>
            """)

            test_counts = (
                data["Test Results"]
                .value_counts()
                .reset_index()
            )

            test_counts.columns = ["Result", "Patients"]

            fig = px.bar(
                test_counts,
                x="Result",
                y="Patients"
            )

            fig.update_traces(
                marker_color="#d97706",
                hovertemplate="<b>%{x}</b><br>Patients: %{y}<extra></extra>"
            )

            fig.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(
                    color="#0f172a",
                    size=12
                ),
                xaxis=dict(
                    title=None,
                    showgrid=False,
                    tickfont=dict(color="#0f172a", size=12)
                ),
                yaxis=dict(
                    title=None,
                    gridcolor="#e2e8f0",
                    tickfont=dict(color="#0f172a", size=12)
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )


def chart_condition_by_gender(data):

    with st.container(border=True):

        render("""
        <div class="chart-title">
            Medical Condition by Gender
        </div>
        """)

        condition_gender = (
            data.groupby(["Medical Condition", "Gender"])
            .size()
            .reset_index(name="Patients")
        )

        fig = px.bar(
            condition_gender,
            x="Medical Condition",
            y="Patients",
            color="Gender",
            barmode="group",
            text="Patients"
        )

        fig.update_traces(
            textposition="outside",
            textfont=dict(color="#0f172a", size=11)  # Color for bar values
        )

        fig.update_layout(
            height=380,
            margin=dict(l=20, r=20, t=20, b=50),
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="#0f172a", size=12),

            xaxis=dict(
                title=dict(text="Medical Condition", font=dict(color="#0f172a", size=13)),
                tickfont=dict(color="#0f172a", size=12),
                showgrid=False
            ),

            yaxis=dict(
                title=dict(text="Number of Patients", font=dict(color="#0f172a", size=13)),
                tickfont=dict(color="#0f172a", size=12),
                gridcolor="#e2e8f0"
            ),

            legend=dict(
                title=dict(text="Gender", font=dict(color="#0f172a", size=12)),
                font=dict(color="#0f172a", size=12)
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )


def section_billing_kpis(data):

    total_billing = data["Billing Amount"].sum()
    avg_billing = data["Billing Amount"].mean()
    highest_billing = data["Billing Amount"].max()
    lowest_billing = data["Billing Amount"].min()

    cols = st.columns(4)

    with cols[0]:
        with st.container(border=True):
            render(f"""
            <div class="metric-card-stacked billing-total">
                <div class="metric-icon">💰</div>
                <div class="metric-label">Total Billing</div>
                <div class="metric-value">${total_billing:,.0f}</div>
                <div class="metric-sub">Overall billing amount</div>
            </div>
            """)

    with cols[1]:
        with st.container(border=True):
            render(f"""
            <div class="metric-card-stacked billing-average">
                <div class="metric-icon">📊</div>
                <div class="metric-label">Average Billing</div>
                <div class="metric-value">${avg_billing:,.2f}</div>
                <div class="metric-sub">Average per patient</div>
            </div>
            """)

    with cols[2]:
        with st.container(border=True):
            render(f"""
            <div class="metric-card-stacked billing-highest">
                <div class="metric-icon">⬆️</div>
                <div class="metric-label">Highest Billing</div>
                <div class="metric-value">${highest_billing:,.2f}</div>
                <div class="metric-sub">Maximum patient bill</div>
            </div>
            """)

    with cols[3]:
        with st.container(border=True):
            render(f"""
            <div class="metric-card-stacked billing-lowest">
                <div class="metric-icon">⬇️</div>
                <div class="metric-label">Lowest Billing</div>
                <div class="metric-value">${lowest_billing:,.2f}</div>
                <div class="metric-sub">Minimum patient bill</div>
            </div>
            """)


def section_billing_charts(data):

    col1, col2 = st.columns(2)

    # =====================================================
    # AVERAGE BILLING BY MEDICAL CONDITION
    # =====================================================

    with col1:
        with st.container(border=True):

            render("""
            <div class="chart-title">
                Average Billing by Medical Condition
            </div>
            """)

            billing_by_condition = (
                data.groupby("Medical Condition")["Billing Amount"]
                .mean()
                .sort_values(ascending=False)
                .reset_index()
            )

            billing_by_condition.columns = [
                "Medical Condition",
                "Average Billing"
            ]

            fig = px.bar(
                billing_by_condition,
                x="Medical Condition",
                y="Average Billing",
                text="Average Billing"
            )

            fig.update_traces(
                marker_color="#0f766e",
                texttemplate="$%{y:,.0f}",
                textposition="outside",
                textfont=dict(
                    color="#0f172a",
                    size=11
                ),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Average Billing: $%{y:,.2f}"
                    "<extra></extra>"
                )
            )

            fig.update_layout(
                height=380,
                margin=dict(l=20, r=20, t=30, b=50),

                paper_bgcolor="white",
                plot_bgcolor="white",

                font=dict(
                    color="#0f172a",
                    size=12
                ),

                xaxis=dict(
                    title=dict(
                        text="Medical Condition",
                        font=dict(
                            color="#0f172a",
                            size=13
                        )
                    ),
                    tickfont=dict(
                        color="#0f172a",
                        size=12
                    ),
                    showgrid=False
                ),

                yaxis=dict(
                    title=dict(
                        text="Average Billing ($)",
                        font=dict(
                            color="#0f172a",
                            size=13
                        )
                    ),
                    tickfont=dict(
                        color="#0f172a",
                        size=12
                    ),
                    gridcolor="#e2e8f0",
                    tickprefix="$",
                    tickformat=",.0f"
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )


    # =====================================================
    # AVERAGE BILLING BY ADMISSION TYPE
    # =====================================================

    with col2:
        with st.container(border=True):

            render("""
            <div class="chart-title">
                Average Billing by Admission Type
            </div>
            """)

            billing_by_admission = (
                data.groupby("Admission Type")["Billing Amount"]
                .mean()
                .sort_values(ascending=False)
                .reset_index()
            )

            billing_by_admission.columns = [
                "Admission Type",
                "Average Billing"
            ]

            fig = px.bar(
                billing_by_admission,
                x="Admission Type",
                y="Average Billing",
                text="Average Billing"
            )

            fig.update_traces(
                marker_color="#d97706",
                texttemplate="$%{y:,.0f}",
                textposition="outside",
                textfont=dict(
                    color="#0f172a",
                    size=11
                ),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Average Billing: $%{y:,.2f}"
                    "<extra></extra>"
                )
            )

            fig.update_layout(
                height=380,
                margin=dict(l=20, r=20, t=30, b=50),

                paper_bgcolor="white",
                plot_bgcolor="white",

                font=dict(
                    color="#0f172a",
                    size=12
                ),

                xaxis=dict(
                    title=dict(
                        text="Admission Type",
                        font=dict(
                            color="#0f172a",
                            size=13
                        )
                    ),
                    tickfont=dict(
                        color="#0f172a",
                        size=12
                    ),
                    showgrid=False
                ),

                yaxis=dict(
                    title=dict(
                        text="Average Billing ($)",
                        font=dict(
                            color="#0f172a",
                            size=13
                        )
                    ),
                    tickfont=dict(
                        color="#0f172a",
                        size=12
                    ),
                    gridcolor="#e2e8f0",
                    tickprefix="$",
                    tickformat=",.0f"
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )


def section_billing_insights(data):

    # Highest-cost medical condition
    condition_billing = (
        data.groupby("Medical Condition")["Billing Amount"]
        .mean()
        .sort_values(ascending=False)
    )

    # Highest-cost admission type
    admission_billing = (
        data.groupby("Admission Type")["Billing Amount"]
        .mean()
        .sort_values(ascending=False)
    )

    highest_condition = (
        condition_billing.index[0]
        if not condition_billing.empty
        else "N/A"
    )

    highest_condition_amount = (
        condition_billing.iloc[0]
        if not condition_billing.empty
        else 0
    )

    highest_admission = (
        admission_billing.index[0]
        if not admission_billing.empty
        else "N/A"
    )

    highest_admission_amount = (
        admission_billing.iloc[0]
        if not admission_billing.empty
        else 0
    )

    # Overall billing
    average_billing = data["Billing Amount"].mean()

    # =====================================================
    # INSIGHTS
    # =====================================================

    with st.container(border=True):

        render("""
        <div class="chart-title">
            💡 Billing Insights
        </div>
        """)

        col1, col2, col3 = st.columns(3)

        with col1:
            render(f"""
            <div class="insight-card">
                <div class="insight-icon">🏥</div>
                <div class="insight-title">Highest-Cost Condition</div>
                <div class="insight-value">{highest_condition}</div>
                <div class="insight-text">
                    Average billing of ${highest_condition_amount:,.2f} per patient.
                </div>
            </div>
            """)

        with col2:
            render(f"""
            <div class="insight-card">
                <div class="insight-icon">🚑</div>
                <div class="insight-title">Highest-Cost Admission</div>
                <div class="insight-value">{highest_admission}</div>
                <div class="insight-text">
                    Average billing of ${highest_admission_amount:,.2f} per patient.
                </div>
            </div>
            """)

        with col3:
            render(f"""
            <div class="insight-card">
                <div class="insight-icon">💵</div>
                <div class="insight-title">Overall Average</div>
                <div class="insight-value">${average_billing:,.2f}</div>
                <div class="insight-text">
                    Average billing amount across filtered patients.
                </div>
            </div>
            """)

def chart_billing_distribution(data):

    with st.container(border=True):

        render("""
        <div class="chart-title">
            Billing Amount Distribution
        </div>
        """)

        fig = px.histogram(
            data,
            x="Billing Amount",
            nbins=20
        )

        fig.update_traces(
            marker_color="#0f766e",
            marker_line_color="white",
            marker_line_width=2,
            hovertemplate=(
        "Billing Range: %{x}<br>"
        "Patients: %{y}"
        "<extra></extra>"
            )
        )

        fig.update_layout(
            height=380,
            margin=dict(l=20, r=20, t=20, b=50),

            paper_bgcolor="white",
            plot_bgcolor="white",

            font=dict(
                color="#0f172a",
                size=12
            ),

            xaxis=dict(
                title=dict(
                    text="Billing Amount ($)",
                    font=dict(
                        color="#0f172a",
                        size=13
                    )
                ),
                tickfont=dict(
                    color="#0f172a",
                    size=12
                ),
                tickprefix="$",
                tickformat=",.0f",
                showgrid=False
            ),

            yaxis=dict(
                title=dict(
                    text="Number of Patients",
                    font=dict(
                        color="#0f172a",
                        size=13
                    )
                ),
                tickfont=dict(
                    color="#0f172a",
                    size=12
                ),
                gridcolor="#e2e8f0"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )


def section_records_table(data, n=None):

    display_columns = [c for c in [
        "Patient ID",
        "Name",
        "Age",
        "Gender",
        "Medical Condition",
        "Admission Type",
        "Billing Amount",
        "Test Results"
    ] if c in data.columns]

    d = data if n is None else data.head(n)

    with st.container(border=True):

        if d.empty:

            render(
                '<div class="empty-state">'
                'No records match the current filters.'
                '</div>'
            )

        else:

            st.dataframe(
                d[display_columns],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Patient ID": st.column_config.TextColumn("Patient ID"),
                    "Name": st.column_config.TextColumn("Patient Name"),
                    "Age": st.column_config.NumberColumn("Age", format="%d"),
                    "Gender": st.column_config.TextColumn("Gender"),
                    "Medical Condition": st.column_config.TextColumn("Medical Condition"),
                    "Admission Type": st.column_config.TextColumn("Admission Type"),
                    "Billing Amount": st.column_config.NumberColumn("Billing Amount", format="$ %.2f"),
                    "Test Results": st.column_config.TextColumn("Test Result"),
                }
            )


def section_patient_detail_lookup(data):

    render('<div class="section-title">Patient Detail Lookup</div>')
    render('<div class="section-subtitle">Select a patient to view their complete profile</div>')

    labels = (
        data["Name"].astype(str)
        + "  •  ID "
        + data["Patient ID"].astype(str)
    ).tolist()

    options = ["Select a patient..."] + labels

    chosen = st.selectbox(
        "🔍 Select Patient",
        options,
        key="patient_lookup"
    )

    if chosen == "Select a patient...":
        render("""
        <div class="panel-card" style="text-align:center; padding:35px;">
            <div style="font-size:35px; margin-bottom:8px;">👤</div>
            <div style="font-size:15px; font-weight:700; color:#0f172a;">
                No Patient Selected
            </div>
            <div style="font-size:12px; color:#64748b; margin-top:5px;">
                Select a patient above to view their complete medical profile.
            </div>
        </div>
        """)
        return

    idx = options.index(chosen) - 1
    prow = data.iloc[idx]

    # Basic patient information
    patient_id = prow["Patient ID"]
    name = prow["Name"]
    age = prow["Age"]
    gender = prow["Gender"]
    condition = prow["Medical Condition"]
    admission = prow["Admission Type"]
    billing = prow["Billing Amount"]
    medication = prow["Medication"]
    test_result = prow["Test Results"]

    # Optional fields
    doctor = prow.get("Doctor", "-") if HAS_DOCTOR else "-"
    hospital = prow.get("Hospital", "-") if HAS_HOSPITAL else "-"
    insurance = prow.get("Insurance Provider", "-") if HAS_INSURANCE else "-"
    room = prow.get("Room Number", "-") if HAS_ROOM else "-"
    blood = prow.get("Blood Type", "-") if HAS_BLOOD else "-"

    # Test result styling
    test_class = badge_for_test_result(test_result)

    # Admission styling
    admission_class = badge_for_admission(admission)

    # Initials
    patient_initials = initials(name)

    # Header
    render(f"""
    <div class="panel-card" style="padding:0; overflow:hidden;">

        <!-- Profile Header -->
        <div style="
            background:linear-gradient(135deg,#0f766e,#0891b2,#2563eb);
            padding:25px 28px;
            color:white;
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:20px;
        ">

            <div style="display:flex; align-items:center; gap:16px;">

                <div style="
                    width:62px;
                    height:62px;
                    border-radius:50%;
                    background:rgba(255,255,255,0.18);
                    border:2px solid rgba(255,255,255,0.45);
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:20px;
                    font-weight:800;
                ">
                    {patient_initials}
                </div>

                <div>
                    <div style="
                        font-size:22px;
                        font-weight:800;
                        margin-bottom:3px;
                    ">
                        {name}
                    </div>

                    <div style="
                        font-size:12px;
                        opacity:0.9;
                    ">
                        Patient ID: {patient_id}
                    </div>
                </div>

            </div>

            <div style="text-align:right;">
                <div style="
                    font-size:11px;
                    opacity:0.75;
                    text-transform:uppercase;
                    letter-spacing:0.7px;
                ">
                    Admission
                </div>

                <div style="
                    margin-top:5px;
                    font-size:13px;
                    font-weight:700;
                ">
                    {admission}
                </div>
            </div>

        </div>

        <!-- Main KPI Cards -->
        <div style="
            padding:22px 25px 10px 25px;
            display:grid;
            grid-template-columns:repeat(4,1fr);
            gap:12px;
        ">

            <div style="
                background:#f8fafc;
                border:1px solid #e2e8f0;
                border-radius:12px;
                padding:14px;
            ">
                <div style="font-size:11px;color:#64748b;">🎂 Age</div>
                <div style="
                    font-size:18px;
                    font-weight:800;
                    color:#0f172a;
                    margin-top:4px;
                ">
                    {age} yrs
                </div>
            </div>

            <div style="
                background:#f8fafc;
                border:1px solid #e2e8f0;
                border-radius:12px;
                padding:14px;
            ">
                <div style="font-size:11px;color:#64748b;">🧑 Gender</div>
                <div style="
                    font-size:18px;
                    font-weight:800;
                    color:#0f172a;
                    margin-top:4px;
                ">
                    {gender}
                </div>
            </div>

            <div style="
                background:#f8fafc;
                border:1px solid #e2e8f0;
                border-radius:12px;
                padding:14px;
            ">
                <div style="font-size:11px;color:#64748b;">💰 Billing</div>
                <div style="
                    font-size:18px;
                    font-weight:800;
                    color:#0f172a;
                    margin-top:4px;
                ">
                    ${billing:,.0f}
                </div>
            </div>

            <div style="
                background:#f8fafc;
                border:1px solid #e2e8f0;
                border-radius:12px;
                padding:14px;
            ">
                <div style="font-size:11px;color:#64748b;">🧪 Test Result</div>
                <div style="margin-top:7px;">
                    <span class="badge {test_class}">
                        {test_result}
                    </span>
                </div>
            </div>

        </div>

        <!-- Medical Information -->
        <div style="padding:10px 25px 25px 25px;">

            <div style="
                font-size:14px;
                font-weight:800;
                color:#0f172a;
                margin:15px 0 10px 0;
            ">
                🩺 Medical Information
            </div>

            <table class="simple-table">

                <tr>
                    <td style="width:190px;color:#64748b;font-weight:600;">
                        Medical Condition
                    </td>
                    <td>
                        <b>{condition}</b>
                    </td>
                </tr>

                <tr>
                    <td style="color:#64748b;font-weight:600;">
                        Admission Type
                    </td>
                    <td>
                        <span class="badge {admission_class}">
                            {admission}
                        </span>
                    </td>
                </tr>

                <tr>
                    <td style="color:#64748b;font-weight:600;">
                        Medication
                    </td>
                    <td>
                        💊 {medication}
                    </td>
                </tr>

                <tr>
                    <td style="color:#64748b;font-weight:600;">
                        Test Result
                    </td>
                    <td>
                        <span class="badge {test_class}">
                            {test_result}
                        </span>
                    </td>
                </tr>

                <tr>
                    <td style="color:#64748b;font-weight:600;">
                        Blood Type
                    </td>
                    <td>
                        🩸 {blood}
                    </td>
                </tr>

            </table>

            <div style="
                font-size:14px;
                font-weight:800;
                color:#0f172a;
                margin:25px 0 10px 0;
            ">
                🏥 Hospital Information
            </div>

            <table class="simple-table">

                <tr>
                    <td style="width:190px;color:#64748b;font-weight:600;">
                        Doctor
                    </td>
                    <td>
                        👨‍⚕️ {doctor}
                    </td>
                </tr>

                <tr>
                    <td style="color:#64748b;font-weight:600;">
                        Hospital
                    </td>
                    <td>
                        🏥 {hospital}
                    </td>
                </tr>

                <tr>
                    <td style="color:#64748b;font-weight:600;">
                        Insurance Provider
                    </td>
                    <td>
                        🛡️ {insurance}
                    </td>
                </tr>

                <tr>
                    <td style="color:#64748b;font-weight:600;">
                        Room Number
                    </td>
                    <td>
                        🚪 {room}
                    </td>
                </tr>

            </table>

        </div>

    </div>
    """)


def section_medical_kpis(data):
    # Total unique medical conditions
    total_conditions = data["Medical Condition"].nunique()

    # Abnormal test percentage
    total_tests = data["Test Results"].notna().sum()
    abnormal_tests = (data["Test Results"] == "Abnormal").sum()

    abnormal_rate = (
        abnormal_tests / total_tests * 100
        if total_tests > 0 else 0
    )

    # Most common medical condition
    condition_counts = data["Medical Condition"].value_counts()

    if not condition_counts.empty:
        top_condition = condition_counts.index[0]
        top_condition_count = condition_counts.iloc[0]
    else:
        top_condition = "N/A"
        top_condition_count = 0

    # Most prescribed medication
    medication_counts = data["Medication"].value_counts()

    if not medication_counts.empty:
        top_medication = medication_counts.index[0]
        top_medication_count = medication_counts.iloc[0]
    else:
        top_medication = "N/A"
        top_medication_count = 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render(f"""
        <div class="metric-card">
            <div class="metric-badge badge-purple">🩺</div>
            <div>
                <div class="metric-label">Medical Conditions</div>
                <div class="metric-value">{total_conditions}</div>
                <div class="trend-up">● Conditions recorded</div>
            </div>
        </div>
        """)

    with col2:
        render(f"""
        <div class="metric-card">
            <div class="metric-badge badge-red">🧪</div>
            <div>
                <div class="metric-label">Abnormal Test Rate</div>
                <div class="metric-value">{abnormal_rate:.1f}%</div>
                <div class="trend-down">● {abnormal_tests:,} abnormal results</div>
            </div>
        </div>
        """)

    with col3:
        render(f"""
        <div class="metric-card">
            <div class="metric-badge badge-teal">🔥</div>
            <div>
                <div class="metric-label">Most Common Condition</div>
                <div class="metric-value" style="font-size:18px;">
                    {top_condition}
                </div>
                <div class="trend-up">● {top_condition_count:,} patients</div>
            </div>
        </div>
        """)

    with col4:
        render(f"""
        <div class="metric-card">
            <div class="metric-badge badge-blue">💊</div>
            <div>
                <div class="metric-label">Top Medication</div>
                <div class="metric-value" style="font-size:18px;">
                    {top_medication}
                </div>
                <div class="trend-up">● {top_medication_count:,} patients</div>
            </div>
        </div>
        """)


# =========================================================
# PAGE ROUTING
# =========================================================

page = st.session_state.page

if page == "Dashboard":
    section_patient_activity(filtered_df)
    render('<div class="section-title">&nbsp;</div>')
    section_medication_and_doctors(filtered_df)
    render('<div class="section-title">Demographics & Conditions</div>')
    section_condition_charts(filtered_df)
    render('<div class="section-title">Billing & Financial Analysis</div>')
    section_billing_charts(filtered_df)
    render('<div class="section-title">Patient Records</div>')
    render('<div class="section-subtitle">Recent patient records from the selected filters</div>')
    section_records_table(filtered_df, n=10)

elif page == "Patients":
    render('<div class="section-title">All Patients</div>')
    render(f'<div class="section-subtitle">{len(filtered_df):,} patients match your filters and search</div>')

    sort_col, dir_col, size_col = st.columns([2, 1, 1])
    sort_options = ["Name", "Age", "Billing Amount", "Medical Condition"] + (["Date of Admission"] if HAS_DATE else [])
    with sort_col:
        sort_by = st.selectbox("Sort by", options=sort_options, key="sort_by")
    with dir_col:
        ascending = st.selectbox("Order", options=["Ascending", "Descending"], key="sort_dir") == "Ascending"
    with size_col:
        page_size = st.selectbox("Rows per page", options=[10, 25, 50, 100], index=1, key="page_size")

    sorted_df = filtered_df.sort_values(sort_by, ascending=ascending).reset_index(drop=True)
    total_pages = max(1, -(-len(sorted_df) // page_size))
    st.session_state.patients_page = min(st.session_state.patients_page, total_pages)

    p1, p2, p3 = st.columns([1, 2, 1])
    with p1:
        if st.button("← Prev", disabled=st.session_state.patients_page <= 1, use_container_width=True):
            st.session_state.patients_page -= 1
            st.rerun()
    with p2:
        render(f'<div style="text-align:center;color:#64748b;font-size:13px;padding-top:8px;">Page {st.session_state.patients_page} of {total_pages}</div>')
    with p3:
        if st.button("Next →", disabled=st.session_state.patients_page >= total_pages, use_container_width=True):
            st.session_state.patients_page += 1
            st.rerun()

    start = (st.session_state.patients_page - 1) * page_size
    page_df = sorted_df.iloc[start:start + page_size]
    section_records_table(page_df)

    section_patient_detail_lookup(sorted_df)

elif page == "Medical Analysis":

    render('<div class="section-title">Medical Analysis</div>')

    render("""
    <div class="section-subtitle">
        Analyze medical conditions, test results, medications, and patient health patterns.
    </div>
    """)

    # Medical KPI cards
    section_medical_kpis(filtered_df)

    # Medical Overview
    render('<div class="section-title">Medical Overview</div>')

    section_condition_charts(filtered_df)

    # Deeper Medical Analysis
    render('<div class="section-title">Condition & Demographic Analysis</div>')

    chart_condition_by_gender(filtered_df)

    # Medication & Doctor Analysis
    render('<div class="section-title">Medication & Doctor Analysis</div>')

    section_medication_and_doctors(filtered_df)

elif page == "Billing":

    render('<div class="section-title">Billing Analysis</div>')

    render("""
    <div class="section-subtitle">
        Analyze patient billing, healthcare costs, and financial patterns.
    </div>
    """)

    # Billing KPI Cards
    section_billing_kpis(filtered_df)

    # Billing Charts
    render('<div class="section-title">Billing Overview</div>')

    section_billing_charts(filtered_df)
    render('<div class="section-title">Financial Insights</div>')

    section_billing_insights(filtered_df)
    render('<div class="section-title">Billing Distribution</div>')

    chart_billing_distribution(filtered_df)

elif page == "Reports":

    render('<div class="section-title">Reports</div>')

    render("""
    <div class="section-subtitle">
        Generate and export reports based on the currently selected patient filters.
    </div>
    """)

    # =========================================================
    # REPORT EXPORTS
    # =========================================================

    render('<div class="section-title">Export Reports</div>')

    col1, col2 = st.columns(2)

    # CSV Export
    with col1:
        with st.container(border=True):

            render("""
            <div class="chart-title">
                📄 CSV Report
            </div>

            <div class="insight-text">
                Download the filtered patient records as a CSV file.
            </div>
            """)

            csv = filtered_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "⬇️ Download CSV",
                data=csv,
                file_name="patient_report.csv",
                mime="text/csv",
                use_container_width=True
            )

    # Excel Export
    with col2:
        with st.container(border=True):

            render("""
            <div class="chart-title">
                📊 Excel Report
            </div>

            <div class="insight-text">
                Download the filtered patient records as an Excel file.
            </div>
            """)

            excel_buffer = BytesIO()

            with pd.ExcelWriter(
                excel_buffer,
                engine="openpyxl"
            ) as writer:

                filtered_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Patient Data"
                )

            st.download_button(
                "⬇️ Download Excel",
                data=excel_buffer.getvalue(),
                file_name="patient_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    # =========================================================
    # REPORT SUMMARY
    # =========================================================

    render('<div class="section-title">Report Summary</div>')

    total_patients = len(filtered_df)

    average_age = (
        filtered_df["Age"].mean()
        if "Age" in filtered_df.columns and not filtered_df.empty
        else 0
    )

    total_billing = (
        filtered_df["Billing Amount"].sum()
        if "Billing Amount" in filtered_df.columns
        else 0
    )

    average_billing = (
        filtered_df["Billing Amount"].mean()
        if "Billing Amount" in filtered_df.columns and not filtered_df.empty
        else 0
    )

    cols = st.columns(4)

    with cols[0]:
        with st.container(border=True):
            render(f"""
            <div class="metric-card-stacked billing-total">
                <div class="metric-icon">👥</div>
                <div class="metric-label">Total Patients</div>
                <div class="metric-value">{total_patients:,}</div>
                <div class="metric-sub">Patients in current report</div>
            </div>
            """)

    with cols[1]:
        with st.container(border=True):
            render(f"""
            <div class="metric-card-stacked billing-average">
                <div class="metric-icon">🎂</div>
                <div class="metric-label">Average Age</div>
                <div class="metric-value">{average_age:.1f}</div>
                <div class="metric-sub">Average patient age</div>
            </div>
            """)

    with cols[2]:
        with st.container(border=True):
            render(f"""
            <div class="metric-card-stacked billing-highest">
                <div class="metric-icon">💰</div>
                <div class="metric-label">Total Billing</div>
                <div class="metric-value">${total_billing:,.0f}</div>
                <div class="metric-sub">Total filtered billing</div>
            </div>
            """)

    with cols[3]:
        with st.container(border=True):
            render(f"""
            <div class="metric-card-stacked billing-lowest">
                <div class="metric-icon">📊</div>
                <div class="metric-label">Average Billing</div>
                <div class="metric-value">${average_billing:,.2f}</div>
                <div class="metric-sub">Average per patient</div>
            </div>
            """)

    # =========================================================
    # REPORT INSIGHTS
    # =========================================================

    render('<div class="section-title">Report Insights</div>')

    with st.container(border=True):

        col1, col2 = st.columns(2)

        # Medical Summary
        with col1:

            if "Medical Condition" in filtered_df.columns and not filtered_df.empty:

                top_condition = (
                    filtered_df["Medical Condition"]
                    .value_counts()
                    .idxmax()
                )

                condition_count = (
                    filtered_df["Medical Condition"]
                    .value_counts()
                    .max()
                )

                render(f"""
                <div class="insight-card">
                    <div class="insight-icon">🏥</div>
                    <div class="insight-title">Medical Summary</div>

                    <div class="insight-text">
                        <b>Most common condition:</b> {top_condition}<br><br>
                        <b>Patients affected:</b> {condition_count:,}
                    </div>
                </div>
                """)

            else:

                render("""
                <div class="insight-card">
                    <div class="insight-icon">🏥</div>
                    <div class="insight-title">Medical Summary</div>

                    <div class="insight-text">
                        No medical condition data available.
                    </div>
                </div>
                """)

        # Financial Summary
        with col2:

            if "Billing Amount" in filtered_df.columns and not filtered_df.empty:

                highest_bill = filtered_df["Billing Amount"].max()
                lowest_bill = filtered_df["Billing Amount"].min()

                render(f"""
                <div class="insight-card">
                    <div class="insight-icon">💰</div>
                    <div class="insight-title">Financial Summary</div>

                    <div class="insight-text">
                        <b>Highest patient bill:</b> ${highest_bill:,.2f}<br><br>
                        <b>Lowest patient bill:</b> ${lowest_bill:,.2f}
                    </div>
                </div>
                """)

            else:

                render("""
                <div class="insight-card">
                    <div class="insight-icon">💰</div>
                    <div class="insight-title">Financial Summary</div>

                    <div class="insight-text">
                        No billing data available.
                    </div>
                </div>
                """)

    # =========================================================
    # REPORT PREVIEW
    # =========================================================

    render('<div class="section-title">Report Preview</div>')

    render("""
    <div class="section-subtitle">
        Preview of the currently filtered patient records.
    </div>
    """)

    with st.container(border=True):

        render("""
        <div class="chart-title">
            📋 Patient Records
        </div>

        <div class="insight-text">
            Preview of the first 25 patient records from the current report.
        </div>
        """)

        section_records_table(filtered_df, n=25)


# =========================================================
# FOOTER
# =========================================================

st.markdown("<hr>", unsafe_allow_html=True)
render("""
<div style="text-align:center; color:#94a3b8; font-size:13px; padding:10px;">
    Healthcare Patient Analytics Dashboard &nbsp;•&nbsp; Built with Python & Streamlit
</div>
""")