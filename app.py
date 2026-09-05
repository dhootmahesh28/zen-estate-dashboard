import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import re

# ── Financial year helpers (Sep → Aug) ──────────────────────────────────────
FY_MONTH_ORDER = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
DEFAULT_MAIN_FY_START = 2025

MONTH_NUM_TO_ABBR = {
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec',
}

MONTH_NAME_MAP = {
    'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
    'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
    'august': 8, 'aug': 8, 'september': 9, 'sept': 9, 'sep': 9,
    'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12,
}


def fy_label(fy_start):
    return f"Sep {fy_start} – Aug {fy_start + 1}"


def month_calendar_year(month_abbr, fy_start):
    return fy_start if month_abbr in ('Sep', 'Oct', 'Nov', 'Dec') else fy_start + 1


def get_fy_start(month_num, year):
    return year if month_num >= 9 else year - 1


def month_label(month_abbr, year):
    return f"{month_abbr} {year}"


def parse_petty_sheet_name(sheet_name):
    """Return (month_abbr, year, month_label) or None if not a monthly petty cash sheet."""
    raw = sheet_name.strip()
    normalized = re.sub(r'[.\-_]+', ' ', raw.lower()).strip()
    normalized = re.sub(r'\s+', ' ', normalized)

    match = re.match(
        r'^(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|'
        r'august|aug|september|sept|sep|october|oct|november|nov|december|dec)\s*'
        r'(20\d{2}|\d{2})?$',
        normalized,
    )
    if not match:
        return None

    month_num = MONTH_NAME_MAP[match.group(1)]
    year_token = match.group(2)
    if year_token:
        year = int(year_token) if len(year_token) == 4 else 2000 + int(year_token)
    else:
        return None

    month_abbr = MONTH_NUM_TO_ABBR[month_num]
    return month_abbr, year, month_label(month_abbr, year)


def sort_month_labels(labels):
    abbr_to_num = {v: k for k, v in MONTH_NUM_TO_ABBR.items()}

    def sort_key(label):
        parts = label.split()
        abbr = parts[0]
        year = int(parts[1])
        month_num = abbr_to_num.get(abbr, 99)
        month_idx = FY_MONTH_ORDER.index(abbr) if abbr in FY_MONTH_ORDER else 99
        return (get_fy_start(month_num, year), month_idx)

    return sorted(labels, key=sort_key)


def filter_df_by_fy(df, fy_start):
    if df is None or df.empty:
        return df.copy() if df is not None else pd.DataFrame()
    if 'FY_Start' in df.columns:
        return df[df['FY_Start'] == fy_start].copy()
    return df.copy()


# Months excluded from petty cash (incomplete / unreliable data)
PETTY_EXCLUDE_MONTHS = {"Aug 2026"}

# Authoritative sheet names in the Petty Cash Excel workbook (Sep 2025 – Jul 2026)
PETTY_CASH_SHEETS = [
    ("September 2025", "Sep 2025"),
    ("October 2025", "Oct 2025"),
    ("November 2025", "Nov 2025"),
    ("December 2025", "Dec 2025"),
    ("January 2026", "Jan 2026"),
    ("Feb.2026", "Feb 2026"),
    ("March 2026", "Mar 2026"),
    ("April 2026", "Apr 2026"),
    ("May 2026", "May 2026"),
    ("June 2026", "Jun 2026"),
    ("July 2026", "Jul 2026"),
]


def filter_petty_by_fy(all_petty, fy_start):
    petty = all_petty.get(fy_start, {})
    if not petty:
        return {}
    labels = sort_month_labels(list(petty.keys()))
    labels = [label for label in labels if label not in PETTY_EXCLUDE_MONTHS]
    return {label: petty[label] for label in labels}


def _format_petty_amount(amount):
    """Format signed petty cash amount for display."""
    if amount < 0:
        return f"-₹{abs(amount):,.0f}"
    if amount > 0:
        return f"₹{amount:,.0f}"
    return "₹0"


def enrich_petty_display(petty_data):
    """
    Chain opening balances month-to-month for display.
    Sep uses Excel opening; each later month opens at the previous month's closing.
    Closing = opening + credited − debited (Total row debits).
    """
    month_keys = list(petty_data.keys())
    enriched = {}
    for i, label in enumerate(month_keys):
        raw = petty_data[label]
        ob = raw["ob"] if i == 0 else enriched[month_keys[i - 1]]["cb"]
        cb = ob + raw["tc"] - raw["td"]
        enriched[label] = {
            "ob": ob,
            "tc": raw["tc"],
            "td": raw["td"],
            "cb": cb,
            "rows": raw["rows"],
        }
    return enriched


def get_available_financial_years(petty_by_fy, df_monthly):
    fys = set(petty_by_fy.keys())
    if df_monthly is not None and not df_monthly.empty and 'FY_Start' in df_monthly.columns:
        fys.update(df_monthly['FY_Start'].dropna().astype(int).tolist())
    if not fys:
        fys.add(DEFAULT_MAIN_FY_START)
    # Show recent financial years only (Sep 2025 onwards)
    fys = {fy for fy in fys if fy >= DEFAULT_MAIN_FY_START}
    if not fys:
        fys.add(DEFAULT_MAIN_FY_START)
    return sorted(fys, reverse=True)

st.set_page_config(
    page_title="Zen Estate Financial Dashboard",
    page_icon="🏢",
    layout="wide"
)

st.markdown("""
    <style>
    /* ── Page background ── */
    .stApp {
        background: linear-gradient(180deg, #eef2ff 0%, #f8fafc 35%, #f1f5f9 100%);
    }

    /* Hide default Streamlit header/footer clutter */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* ── Main title ── */
    .main-header {
        font-size: 2.35rem;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        padding: 1.35rem 1.5rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 45%, #2563eb 100%);
        margin-bottom: 1.25rem;
        letter-spacing: 0.03em;
        text-shadow: 0 3px 12px rgba(0,0,0,0.45);
        border: 2px solid rgba(255,255,255,0.15);
        box-shadow: 0 10px 30px rgba(30, 58, 138, 0.35);
        -webkit-text-fill-color: #ffffff;
    }

    /* ── Financial year control panel banner ── */
    .fy-panel-banner {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 55%, #60a5fa 100%);
        color: #fff;
        padding: 14px 20px;
        border-radius: 14px 14px 0 0;
        font-size: 1.05rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 0;
        box-shadow: inset 0 -2px 0 rgba(255,255,255,0.2);
    }

    /* ── Active FY badge ── */
    .fy-active-badge {
        display: inline-block;
        background: linear-gradient(135deg, #059669, #10b981);
        color: #fff;
        font-weight: 800;
        font-size: 0.95rem;
        padding: 10px 20px;
        border-radius: 999px;
        margin: 0.75rem 0 1rem 0;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.45);
        border: 2px solid rgba(255,255,255,0.35);
        letter-spacing: 0.02em;
    }

    /* ── Section headers ── */
    .sec-header {
        color: white;
        padding: 12px 20px;
        border-radius: 12px;
        font-size: 1.08rem;
        font-weight: 800;
        margin: 1.2rem 0 0.8rem 0;
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: 0.03em;
        box-shadow: 0 4px 14px rgba(0,0,0,0.12);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .sec-blue   { background: linear-gradient(90deg, #1e40af, #3b82f6); }
    .sec-green  { background: linear-gradient(90deg, #166534, #22c55e); }
    .sec-purple { background: linear-gradient(90deg, #5b21b6, #8b5cf6); }
    .sec-orange { background: linear-gradient(90deg, #c2410c, #f97316); }
    .sec-pink   { background: linear-gradient(90deg, #be185d, #ec4899); }
    .sec-teal   { background: linear-gradient(90deg, #0f766e, #14b8a6); }

    /* ── Metric cards ── */
    .metric-row { display: flex; gap: 14px; margin-bottom: 1.1rem; }
    .metric-card {
        flex: 1;
        border-radius: 14px;
        padding: 16px 18px;
        color: white;
        min-width: 0;
        box-shadow: 0 8px 22px rgba(0,0,0,0.18);
        border: 1px solid rgba(255,255,255,0.22);
        transition: transform 0.15s ease;
    }
    .metric-card:hover { transform: translateY(-2px); }
    .mc-blue   { background: linear-gradient(145deg, #1d4ed8, #3b82f6); }
    .mc-green  { background: linear-gradient(145deg, #15803d, #22c55e); }
    .mc-amber  { background: linear-gradient(145deg, #b45309, #f59e0b); }
    .mc-red    { background: linear-gradient(145deg, #b91c1c, #ef4444); }
    .metric-label {
        font-size: 0.72rem;
        opacity: 0.92;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
        font-weight: 700;
    }
    .metric-value { font-size: 1.45rem; font-weight: 800; text-shadow: 0 1px 3px rgba(0,0,0,0.2); }
    .metric-sub   { font-size: 0.72rem; opacity: 0.88; margin-top: 5px; font-weight: 600; }

    /* ── Streamlit tabs styling ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: linear-gradient(135deg, #e0e7ff, #dbeafe);
        padding: 10px 12px;
        border-radius: 14px;
        border: 2px solid #93c5fd;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.15);
    }
    .stTabs [data-baseweb="tab"] {
        height: 52px;
        white-space: pre-wrap;
        background-color: rgba(255,255,255,0.65);
        border-radius: 10px;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        color: #1e3a8a !important;
        border: 2px solid transparent !important;
        padding: 8px 16px !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1e40af, #2563eb) !important;
        color: #ffffff !important;
        border: 2px solid #1d4ed8 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.25rem;
    }

    /* ── Petty cash month picker highlight ── */
    [data-testid="stVerticalBlockBorderWrapper"]:has(#petty-picker-marker) {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 50%, #FCD34D 100%) !important;
        border: 3px solid #D97706 !important;
        border-radius: 14px !important;
        padding: 18px 22px 14px 22px !important;
        margin: 1.2rem 0 1rem 0 !important;
        box-shadow: 0 6px 18px rgba(217, 119, 6, 0.35) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(#petty-picker-marker) [data-testid="stSelectbox"] label p {
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        color: #92400E !important;
        letter-spacing: 0.02em !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(#petty-picker-marker) div[data-baseweb="select"] > div {
        background: #FFFFFF !important;
        border: 2px solid #B45309 !important;
        border-radius: 10px !important;
        min-height: 50px !important;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.06), 0 0 0 3px rgba(251, 191, 36, 0.45) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(#petty-picker-marker) div[data-baseweb="select"] > div > div {
        font-size: 1.08rem !important;
        font-weight: 700 !important;
        color: #78350F !important;
    }

    /* ── Financial year selector highlight ── */
    [data-testid="stVerticalBlockBorderWrapper"]:has(#fy-picker-marker) {
        background: linear-gradient(180deg, #eff6ff 0%, #dbeafe 100%) !important;
        border: 3px solid #2563EB !important;
        border-radius: 16px !important;
        padding: 0 22px 18px 22px !important;
        margin: 0 0 0.5rem 0 !important;
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.28) !important;
        overflow: hidden;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(#fy-picker-marker) [data-testid="stSelectbox"] label p {
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        color: #1E3A8A !important;
        letter-spacing: 0.03em !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(#fy-picker-marker) div[data-baseweb="select"] > div {
        background: #FFFFFF !important;
        border: 2px solid #1D4ED8 !important;
        border-radius: 12px !important;
        min-height: 54px !important;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05), 0 0 0 4px rgba(59, 130, 246, 0.25) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(#fy-picker-marker) div[data-baseweb="select"] > div > div {
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        color: #1e3a8a !important;
    }

    /* ── Streamlit metrics in tabs ── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8fafc, #eef2ff);
        padding: 12px 16px;
        border-radius: 12px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    [data-testid="stMetricLabel"] {
        font-weight: 700 !important;
        color: #475569 !important;
    }
    [data-testid="stMetricValue"] {
        font-weight: 800 !important;
        color: #0f172a !important;
    }

    /* ── Dataframe headers — ALL tables ── */
    div[data-testid="stDataFrame"] table th,
    .dataframe th,
    .col_heading {
        text-align: center !important;
        background: linear-gradient(135deg, #1a1a6e, #1f77b4) !important;
        color: white !important;
        font-weight: bold !important;
        padding: 12px !important;
        font-size: 1.0rem !important;
        letter-spacing: 0.03em !important;
    }
    div[data-testid="stDataFrame"] table td,
    .dataframe td,
    .data {
        text-align: center !important;
        padding: 10px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="stDataFrame"] table tbody tr:nth-child(even) td {
        background-color: #f1f5f9 !important;
    }
    div[data-testid="stDataFrame"] table tbody tr:hover td {
        background-color: #e0e7ff !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_excel_from_github():
    """Load Excel file directly from GitHub repository"""
    # GitHub raw file URL - UPDATE THIS with your actual file URL
    GITHUB_EXCEL_URL = "https://raw.githubusercontent.com/dhootmahesh28/zen-estate-dashboard/master/Zen_Estate_Combined_Expenses_Q1.xlsx"
    
    try:
        import requests
        from io import BytesIO
        
        # Download the file
        response = requests.get(GITHUB_EXCEL_URL)
        response.raise_for_status()
        
        # Load into pandas
        excel_file = BytesIO(response.content)
        return load_excel_data(excel_file)
    except Exception as e:
        st.error(f"Error loading data from GitHub: {e}")
        st.info("Please make sure the Excel file is uploaded to your GitHub repository.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

PETTY_CASH_URL = (
    "https://raw.githubusercontent.com/dhootmahesh28/zen-estate-dashboard/master/"
    "Petty_Cash_Expense_Details.xlsx"
)

# Sheets that are not monthly petty cash ledgers
PETTY_SKIP_SHEETS = {
    'summary sheet', 'sheet14', 'h wing', 'e wing electrical work',
    '15th aug-23', '22th jan-24', '26th jan-24', 'holi event 26th mar-24',
    '15 aug-24', '15th-08-2024',
}


def _format_petty_date(val):
    if pd.isna(val) or val == "":
        return ""
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.strftime("%d-%b-%y")
    if isinstance(val, (int, float)) and val > 40000:
        return (pd.Timestamp("1899-12-30") + pd.Timedelta(days=int(val))).strftime("%d-%b-%y")
    return str(val).strip()


def _parse_petty_month_sheet(df):
    """Parse one monthly petty cash sheet (header=None layout)."""
    opening = 0.0
    total_credit = 0.0
    total_debit = 0.0
    excel_total_dr = None
    rows = []
    sr = 0

    for idx in range(len(df)):
        row = df.iloc[idx]
        particulars = (
            str(row.iloc[2]).strip()
            if len(row) > 2 and pd.notna(row.iloc[2])
            else ""
        )
        whom = (
            str(row.iloc[3]).strip()
            if len(row) > 3 and pd.notna(row.iloc[3])
            else ""
        )
        vr_type = (
            str(row.iloc[4]).strip()
            if len(row) > 4 and pd.notna(row.iloc[4])
            else ""
        )
        credit = (
            float(row.iloc[5])
            if len(row) > 5 and pd.notna(row.iloc[5]) and isinstance(row.iloc[5], (int, float))
            else 0.0
        )
        debit = (
            float(row.iloc[6])
            if len(row) > 6 and pd.notna(row.iloc[6]) and isinstance(row.iloc[6], (int, float))
            else 0.0
        )
        date_val = row.iloc[1] if len(row) > 1 else ""

        if whom == "Opening Balance":
            opening = credit if credit != 0 else (-debit if debit > 0 else debit)
            continue

        if particulars == "Total" or whom == "Total":
            excel_total_dr = debit
            continue

        # Summary row without a "Total" label (some sheets use a blank particulars cell)
        if not particulars and not whom and credit and debit:
            excel_total_dr = debit
            continue

        if "Closing Balance" in particulars:
            continue

        if not particulars and not whom and credit == 0 and debit == 0:
            continue

        sr += 1
        total_credit += credit
        total_debit += debit
        rows.append([
            str(sr),
            _format_petty_date(date_val),
            particulars,
            whom,
            vr_type,
            credit if credit else "",
            debit if debit else "",
        ])

    tc = total_credit
    td = excel_total_dr if excel_total_dr is not None else total_debit
    cb = opening + tc - td

    return {
        "ob": opening,
        "tc": tc,
        "td": td,
        "cb": cb,
        "rows": rows,
    }


@st.cache_data(show_spinner=False, ttl=300)
def load_petty_cash_data(cache_bust=0):
    """Load petty cash monthly sheets (Sep 2025 – Jul 2026), grouped by financial year."""
    try:
        import io
        import requests

        url = PETTY_CASH_URL
        if cache_bust:
            url = f"{PETTY_CASH_URL}?v={cache_bust}"

        response = requests.get(
            url,
            timeout=30,
            headers={"Cache-Control": "no-cache", "Pragma": "no-cache"},
        )
        response.raise_for_status()
        xl = pd.ExcelFile(io.BytesIO(response.content))

        petty_by_fy = {}
        abbr_to_num = {v: k for k, v in MONTH_NUM_TO_ABBR.items()}

        for sheet_name, label in PETTY_CASH_SHEETS:
            if sheet_name not in xl.sheet_names:
                continue
            month_abbr, year_str = label.split()
            fy_start = get_fy_start(abbr_to_num[month_abbr], int(year_str))
            df = xl.parse(sheet_name, header=None)
            parsed_sheet = _parse_petty_month_sheet(df)
            petty_by_fy.setdefault(fy_start, {})[label] = parsed_sheet

        return petty_by_fy
    except Exception:
        return {}


@st.cache_data(show_spinner=False)
def load_leela_data():
    """Load Leela Fund expenditure data from Sheet5 (col C=description, col D=amount)."""
    try:
        import requests, io
        url = "https://raw.githubusercontent.com/dhootmahesh28/zen-estate-dashboard/master/Zen_Estate_Combined_Expenses_Q1.xlsx"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        df = pd.read_excel(io.BytesIO(response.content), sheet_name='Sheet5', header=None)
        
        items = []
        for row in range(df.shape[0]):
            # Description in col C (index 2), Amount in col D (index 3)
            desc = df.iloc[row, 2] if df.shape[1] > 2 else None
            amt  = df.iloc[row, 3] if df.shape[1] > 3 else None
            if pd.notna(desc) and isinstance(desc, str) and desc.strip():
                items.append({
                    'Description': desc.strip(),
                    'Amount': float(amt) if pd.notna(amt) and isinstance(amt, (int, float)) else None
                })
        return pd.DataFrame(items)
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_excel_data(file):
    """Load all financial data from Excel"""
    try:
        df = pd.read_excel(file, sheet_name='Sheet1', header=None)
        
        # Wing names from columns 6-21
        wings = ['A Wing', 'A Shop', 'B Wing', 'B Shop', 'C Wing', 'C Shop Total', 
                 'C Shop Rahul', 'C Shop Sagar', 'D Wing', 'D Shop', 'E Wing', 'E Shop', 
                 'F Wing', 'G Wing', 'H Wing', 'I Wing']
        
        # Extract monthly data
        months_info = [
            {'name': 'Sep', 'to_be_row': 9, 'received_row': 8, 'diff_row': 10, 'summary_row': 14, 'expense_col': 15},
            {'name': 'Oct', 'to_be_row': 29, 'received_row': 28, 'diff_row': 30, 'summary_row': 34, 'expense_col': 15},
            {'name': 'Nov', 'to_be_row': 45, 'received_row': 44, 'diff_row': 46, 'summary_row': 50, 'expense_col': 15},
            {'name': 'Dec', 'to_be_row': 62, 'received_row': 61, 'diff_row': 63, 'summary_row': 67, 'expense_col': 15},
            {'name': 'Jan', 'to_be_row': 77, 'received_row': 76, 'diff_row': 78, 'summary_row': 82, 'expense_col': 15},
            {'name': 'Feb', 'to_be_row': 95, 'received_row': 94, 'diff_row': 96, 'summary_row': 100, 'expense_col': 15},
            {'name': 'Mar', 'to_be_row': 111, 'received_row': 110, 'diff_row': 112, 'summary_row': 116, 'expense_col': 15},
            {'name': 'Apr', 'to_be_row': 128, 'received_row': 127, 'diff_row': 129, 'summary_row': 133, 'expense_col': 15},
            {'name': 'May', 'to_be_row': 147, 'received_row': 146, 'diff_row': 148, 'summary_row': 152, 'expense_col': 15},
            {'name': 'Jun', 'to_be_row': 166, 'received_row': 165, 'diff_row': 167, 'summary_row': 171, 'expense_col': 15},
            {'name': 'Jul', 'to_be_row': 182, 'received_row': 181, 'diff_row': 183, 'summary_row': 187, 'expense_col': 15}
        ]
        
        # Monthly summary data
        monthly_data = []
        wing_data = []
        
        for month_info in months_info:
            month = month_info['name']
            fy_start = DEFAULT_MAIN_FY_START
            cal_year = month_calendar_year(month, fy_start)
            
            # Get summary totals
            to_be = df.iloc[month_info['summary_row'], 6] if pd.notna(df.iloc[month_info['summary_row'], 6]) else 0
            received = df.iloc[month_info['summary_row'], 9] if pd.notna(df.iloc[month_info['summary_row'], 9]) else 0
            expense = df.iloc[month_info['summary_row'], month_info['expense_col']] if pd.notna(df.iloc[month_info['summary_row'], month_info['expense_col']]) else 0
            
            # Compute Extra Income from breakdown row (sum cols 23-28) to match breakdown table
            breakdown_row_map = {
                'Sep': 8, 'Oct': 28, 'Nov': 44, 'Dec': 61, 'Jan': 76,
                'Feb': 94, 'Mar': 110, 'Apr': 127, 'May': 146, 'Jun': 165, 'Jul': 181
            }
            br = breakdown_row_map.get(month, month_info['summary_row'])
            extra_income = sum(
                float(df.iloc[br, c]) if pd.notna(df.iloc[br, c]) and isinstance(df.iloc[br, c], (int, float)) else 0
                for c in [23, 24, 25, 26, 27, 28]
            )
            
            monthly_data.append({
                'Month': month,
                'Year': cal_year,
                'FY_Start': fy_start,
                'To_Be': float(to_be),
                'Received': float(received),
                'Expense': float(expense),
                'Extra_Income': float(extra_income)
            })
            
            # Get wing-wise data
            for idx, wing in enumerate(wings):
                col_idx = 6 + idx
                if col_idx < df.shape[1]:
                    to_be_val = df.iloc[month_info['to_be_row'], col_idx]
                    received_val = df.iloc[month_info['received_row'], col_idx]
                    diff_val = df.iloc[month_info['diff_row'], col_idx]
                    
                    wing_data.append({
                        'Month': month,
                        'Year': cal_year,
                        'FY_Start': fy_start,
                        'Wing': wing,
                        'To_Be': float(to_be_val) if pd.notna(to_be_val) else 0,
                        'Received': float(received_val) if pd.notna(received_val) else 0,
                        'Difference': float(diff_val) if pd.notna(diff_val) else 0
                    })
        
        # Get vendor data for ALL months (Sep, Oct, Nov, Dec, Jan)
        vendor_data = []
        
        # Define vendor sections for each month
        vendor_sections = [
            {'month': 'Sep', 'start': 3, 'end': 20},     # Sep vendor rows
            {'month': 'Oct', 'start': 22, 'end': 36},    # Oct vendor rows  
            {'month': 'Nov', 'start': 38, 'end': 52},    # Nov vendor rows
            {'month': 'Dec', 'start': 55, 'end': 68},    # Dec vendor rows
            {'month': 'Jan', 'start': 70, 'end': 85},    # Jan vendor rows
            {'month': 'Feb', 'start': 88, 'end': 102},   # Feb vendor rows
            {'month': 'Mar', 'start': 104, 'end': 118},  # Mar vendor rows
            {'month': 'Apr', 'start': 121, 'end': 133},
            {'month': 'May', 'start': 139, 'end': 152}    # May vendor rows
        ]
        
        for section in vendor_sections:
            for idx in range(section['start'], min(section['end'], len(df))):
                vendor = df.iloc[idx, 2]
                amount = df.iloc[idx, 3]
                if pd.notna(vendor) and pd.notna(amount) and isinstance(amount, (int, float)) and amount > 0:
                    # Check if vendor name is not a header
                    vendor_str = str(vendor)
                    if 'Vendor Name' not in vendor_str and 'Vendor Bills' not in vendor_str:
                        vendor_data.append({
                            'Vendor': vendor_str,
                            'Amount': float(amount),
                            'Month': section['month'],
                            'FY_Start': DEFAULT_MAIN_FY_START,
                        })
        
        df_monthly = pd.DataFrame(monthly_data)
        df_wings = pd.DataFrame(wing_data)
        df_vendors = pd.DataFrame(vendor_data) if vendor_data else pd.DataFrame()
        
        # Extract Extra Income breakdown by source
        # Using specific rows: Sep=9, Oct=29, Nov=45, Dec=62, Jan=77 (Excel rows)
        # Columns: NBH=23(X), Lift=24(Y), Event=25(Z), Scrap=26(AA)
        extra_income_breakdown = []
        
        month_rows = {
            'Sep': 8,    # Total row for extra income breakdown
            'Oct': 28,
            'Nov': 44,
            'Dec': 61,
            'Jan': 76,
            'Feb': 94,   # Total row for Feb
            'Mar': 110,  # Total row for Mar
            'Apr': 127,  # Total row for Apr
            'May': 146,  # Total row for May
            'Jun': 165,  # Total row for Jun
            'Jul': 181   # Total row for Jul
        }
        
        for month, row_idx in month_rows.items():
            if row_idx < len(df):
                nbh = df.iloc[row_idx, 23] if pd.notna(df.iloc[row_idx, 23]) else 0
                lift = df.iloc[row_idx, 24] if pd.notna(df.iloc[row_idx, 24]) else 0
                event = df.iloc[row_idx, 25] if pd.notna(df.iloc[row_idx, 25]) else 0
                scrap = df.iloc[row_idx, 26] if pd.notna(df.iloc[row_idx, 26]) else 0
                parking_fine = df.iloc[row_idx, 27] if pd.notna(df.iloc[row_idx, 27]) else 0
                clubhouse = df.iloc[row_idx, 28] if pd.notna(df.iloc[row_idx, 28]) else 0
                
                extra_income_breakdown.append({
                    'Month': month,
                    'FY_Start': DEFAULT_MAIN_FY_START,
                    'NBH': float(nbh) if isinstance(nbh, (int, float)) else 0,
                    'Lift': float(lift) if isinstance(lift, (int, float)) else 0,
                    'Event': float(event) if isinstance(event, (int, float)) else 0,
                    'Scrap': float(scrap) if isinstance(scrap, (int, float)) else 0,
                    'Parking_Fine': float(parking_fine) if isinstance(parking_fine, (int, float)) else 0,
                    'ClubHouse_Booking & Gym': float(clubhouse) if isinstance(clubhouse, (int, float)) else 0,
                })
        
        df_extra_income_breakdown = pd.DataFrame(extra_income_breakdown)
        
        # Extract Fine data
        # Structure: Col 30 = Vendor name (HK/Quinteze/Security/STP)
        # Cols 31-44 = Wing/Shop amounts: 31=A Wing, 32=B Wing, 33=C Wing, 34=D Wing,
        #              35=E Wing, 36=F Wing, 37=G Wing, 38=H Wing, 39=I Wing,
        #              40=A Shop, 41=B Shop, 42=C Shop Total, 43=D Shop, 44=E Shop
        # Each month: Vendors header row, then +1=HK, +2=Quinteze, +3=Security, +4=STP
        
        fine_col_map = {
            31: 'A Wing', 32: 'B Wing', 33: 'C Wing', 34: 'D Wing', 35: 'E Wing',
            36: 'F Wing', 37: 'G Wing', 38: 'H Wing', 39: 'I Wing',
            40: 'A Shop', 41: 'B Shop', 42: 'C Shop Total', 43: 'D Shop', 44: 'E Shop'
        }
        
        fine_sections = [
            {'month': 'Sep', 'vendor_row': 2},
            {'month': 'Oct', 'vendor_row': 21},
            {'month': 'Nov', 'vendor_row': 37},
            {'month': 'Dec', 'vendor_row': 54},
            {'month': 'Jan', 'vendor_row': 69},
            {'month': 'Feb', 'vendor_row': 87},
            {'month': 'Mar', 'vendor_row': 103},
            {'month': 'Apr', 'vendor_row': 120},
            {'month': 'May', 'vendor_row': 138},
            {'month': 'Jun', 'vendor_row': 157},
            {'month': 'Jul', 'vendor_row': 173}
        ]
        
        fine_data = {}  # keyed by (month, wing)
        
        for section in fine_sections:
            month = section['month']
            vr = section['vendor_row']
            # Rows: vr+1=HK, vr+2=Quinteze, vr+3=Security, vr+4=STP
            vendor_rows = {'HK': vr+1, 'Quinteze': vr+2, 'Security': vr+3, 'STP': vr+4}
            
            for vendor, row_idx in vendor_rows.items():
                if row_idx >= len(df):
                    continue
                for col, wing in fine_col_map.items():
                    if col >= df.shape[1]:
                        continue
                    val = df.iloc[row_idx, col]
                    amount = float(val) if pd.notna(val) and isinstance(val, (int, float)) and val != 0 else 0
                    if amount != 0:
                        key = (month, wing)
                        if key not in fine_data:
                            fine_data[key] = {
                                'Month': month, 'Wing': wing, 'FY_Start': DEFAULT_MAIN_FY_START,
                                'HK': 0, 'Quinteze': 0, 'Security': 0, 'STP': 0,
                            }
                        fine_data[key][vendor] += amount
        
        # Convert to dataframe
        fine_rows = []
        for key, row in fine_data.items():
            row['Total_Fine'] = row['HK'] + row['Quinteze'] + row['Security'] + row['STP']
            fine_rows.append(row)
        
        df_fines = pd.DataFrame(fine_rows) if fine_rows else pd.DataFrame()
        
        return df_monthly, df_wings, df_vendors, df_extra_income_breakdown, df_fines
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def create_vendor_breakdown(df_vendors, month):
    """Vendor Expense Breakdown with color gradient for a specific month"""
    if df_vendors.empty:
        return None
    
    # Filter by month
    month_vendors = df_vendors[df_vendors['Month'] == month].copy()
    
    if month_vendors.empty:
        return None
    
    # Sort by amount
    month_vendors = month_vendors.sort_values('Amount', ascending=False)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=month_vendors['Vendor'],
        y=month_vendors['Amount'],
        marker=dict(
            color=month_vendors['Amount'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Amount Paid")
        ),
        text=[f'₹{v:,.2f}' for v in month_vendors['Amount']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Amount: ₹%{y:,.2f}<extra></extra>'
    ))
    
    # Set the year based on month
    year = "2026" if month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"] else "2025"
    
    fig.update_layout(
        title=f'Vendor Expense Breakdown ({month} {year})',
        xaxis_title='Vendor',
        yaxis_title='Amount (INR)',
        height=500,
        plot_bgcolor='#E5ECF6',
        yaxis=dict(tickprefix='₹', tickformat=',.2f')
    )
    
    return fig

def create_extra_income_chart(df_monthly):
    """Extra Income Month-wise Bar Chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_monthly['Month'],
        y=df_monthly['Extra_Income'],
        marker_color='#FFA15A',
        text=[f'₹{v:,.0f}' for v in df_monthly['Extra_Income']],
        textposition='outside',
        textfont=dict(size=12),
        hovertemplate='<b>%{x}</b><br>Extra Income: ₹%{y:,.0f}<extra></extra>'
    ))
    
    # Calculate max value for proper y-axis range
    max_value = df_monthly['Extra_Income'].max()
    
    fig.update_layout(
        title='Extra Income by Month',
        xaxis_title='Month',
        yaxis_title='Amount (INR)',
        height=420,
        yaxis=dict(
            tickprefix='₹', 
            tickformat=',.0f',
            range=[0, max_value * 1.15]  # Add 15% padding for text visibility
        )
    )
    
    return fig

def create_combined_monthly_chart(df_monthly):
    """Combined Month-wise Line Chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_monthly['Month'],
        y=df_monthly['To_Be'],
        mode='lines+markers',
        name='To Be',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=10)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_monthly['Month'],
        y=df_monthly['Received'],
        mode='lines+markers',
        name='Received',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=10)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_monthly['Month'],
        y=df_monthly['Expense'],
        mode='lines+markers',
        name='Expenses (Total)',
        line=dict(color='#EF553B', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title='Combined Month-wise — To Be, Received, Expenses',
        xaxis_title='Month',
        yaxis_title='Amount (INR)',
        height=520,
        yaxis=dict(tickprefix='₹', tickformat=',.0f')
    )
    
    return fig

def create_wing_difference_chart(df_wings):
    """Pending/Excess Amount by Wing/Shop"""
    # Aggregate total difference per wing across all months
    wing_totals = df_wings.groupby('Wing')['Difference'].sum().reset_index()
    
    # Flip the values for display (multiply by -1)
    # So pending (positive) shows below, excess (negative) shows above
    wing_totals['Display_Value'] = wing_totals['Difference'] * -1
    
    # Create color array: Positive original = RED (pending), Negative original = GREEN (excess)
    colors = []
    for diff in wing_totals['Difference']:
        if diff > 0:
            colors.append('#d62728')  # Red for pending (positive means money owed)
        elif diff < 0:
            colors.append('#2ca02c')  # Green for excess (negative means overpaid)
        else:
            colors.append('#9e9e9e')  # Gray
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=wing_totals['Wing'],
        y=wing_totals['Display_Value'],  # Use flipped values
        marker_color=colors,
        text=[f'₹{v:,.2f}' for v in wing_totals['Difference']],  # Show original values in labels
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Difference: ₹%{text}<extra></extra>',
        customdata=wing_totals['Difference']
    ))
    
    fig.update_layout(
        title='Pending (red) / Excess (green)',
        xaxis_title='Wing / Shop',
        yaxis_title='Amount (INR)',
        height=520,
        plot_bgcolor='#E5ECF6',
        yaxis=dict(tickprefix='₹', tickformat=',.2f'),
        margin=dict(t=48, r=24, b=96, l=56)
    )
    
    return fig

# Column header colours for each table type
HEADER_COLORS = {
    'default':              'linear-gradient(135deg,#1a1a6e,#1f77b4)',
    'Month':                '#555555',
    'Wing':                 '#555555',
    'NBH':                  '#185FA5',
    'Lift':                 '#7F77DD',
    'Event':                '#1D9E75',
    'Scrap':                '#BA7517',
    'Parking_Fine':         '#D85A30',
    'ClubHouse_Booking & Gym': '#D4537E',
    'Total':                '#3B6D11',
    'To Be Received':       '#185FA5',
    'To_Be':                '#185FA5',
    'Actual Received':      '#1D9E75',
    'Received':             '#1D9E75',
    'Difference':           '#A32D2D',
    'Expense':              '#BA7517',
    'Extra_Income':         '#D4537E',
    'Fine_Details':         '#D85A30',
    'Pending/Excess (-ve = Excess)': '#A32D2D',
}

MONTH_COLORS = {
    'Sep': '#cce5ff', 'Oct': '#ffe5cc', 'Nov': '#d9ccff', 'Dec': '#fff0b3',
    'Jan': '#ffccdd', 'Feb': '#b3f0e0', 'Mar': '#fff3b3', 'Apr': '#ccf0cc', 'May': '#f0ccff', 'Jun': '#ffd6cc', 'Jul': '#ccf5ff',
}

def render_html_table(df, fmt=None):
    """Render a DataFrame as an HTML table with coloured headers and month row shading."""
    fmt = fmt or {}
    
    # Build header row
    th_cells = '<th style="padding:10px 14px;text-align:center;color:white;font-weight:bold;font-size:0.95rem;background:linear-gradient(135deg,#1a1a6e,#1f77b4);">&#8203;</th>'  # index col
    for col in df.columns:
        bg = HEADER_COLORS.get(col, HEADER_COLORS['default'])
        th_cells += f'<th style="padding:10px 14px;text-align:center;color:white;font-weight:bold;font-size:0.95rem;background:{bg};">{col}</th>'
    
    # Build data rows
    rows_html = ''
    for _, row in df.iterrows():
        month_val = row.get('Month', '')
        row_bg = MONTH_COLORS.get(str(month_val), '#ffffff')
        td_cells = f'<td style="padding:9px 14px;text-align:center;background:{row_bg};font-size:0.9rem;color:#444;"></td>'  # index
        for col in df.columns:
            val = row[col]
            fmt_val = fmt.get(col, '{}').format(val) if col in fmt else str(val) if not isinstance(val, float) else f'{val:,.2f}'
            # Difference / Pending column colouring
            cell_style = f'padding:9px 14px;text-align:center;background:{row_bg};font-size:0.9rem;'
            if col in ('Difference', 'Pending/Excess (-ve = Excess)'):
                try:
                    num = float(val)
                    if num < 0:
                        cell_style += 'background:#ccffcc !important;color:#2a6e00;font-weight:bold;'
                    elif num > 0:
                        cell_style += 'background:#ffcccc !important;color:#8b0000;font-weight:bold;'
                    else:
                        cell_style += 'background:#ffffcc !important;color:#555;'
                except (ValueError, TypeError):
                    pass
            td_cells += f'<td style="{cell_style}">{fmt_val}</td>'
        rows_html += f'<tr>{td_cells}</tr>'
    
    html = f"""
    <div style="overflow-x:auto;border-radius:10px;border:1px solid #ddd;margin-bottom:1rem;">
    <table style="width:100%;border-collapse:collapse;">
      <thead><tr>{th_cells}</tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_leela_fund(df_leela):
    """Render the Leela Fund Details section."""
    st.markdown("<div class='sec-header' style='background:linear-gradient(90deg,#5B4FCF,#9B59B6);margin-top:1.5rem;'>🏦 Leela Fund Details</div>", unsafe_allow_html=True)
    
    try:
        if df_leela is not None and not df_leela.empty:
            leela_total   = 2800000
            leela_items   = df_leela.dropna(subset=['Amount']).copy()
            total_spent   = leela_items['Amount'].sum()
            balance       = leela_total - total_spent
            pct_spent     = (total_spent / leela_total) * 100
            pct_left      = 100 - pct_spent
            
            # Top 3 metric cards
            st.markdown(f"""
            <div class='metric-row'>
              <div class='metric-card' style='background:linear-gradient(135deg,#5B4FCF,#9B59B6);'>
                <div class='metric-label'>Total Received from Leela</div>
                <div class='metric-value'>₹{leela_total/100000:.0f} Lakh</div>
                <div class='metric-sub'>One-time corpus fund</div>
              </div>
              <div class='metric-card mc-red'>
                <div class='metric-label'>Total Utilised</div>
                <div class='metric-value'>₹{total_spent:,.0f}</div>
                <div class='metric-sub'>{pct_spent:.2f}% of fund used</div>
              </div>
              <div class='metric-card mc-green'>
                <div class='metric-label'>Available Balance</div>
                <div class='metric-value'>₹{balance:,.0f}</div>
                <div class='metric-sub'>{pct_left:.2f}% remaining</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Build HTML table with running balance
            th_html = ''
            for col, bg in [('#','#555'), ('Description','#5B4FCF'),
                             ('Amount Spent (₹)','#A32D2D'),
                             ('Running Balance (₹)','#1D6B3B'),
                             ('Status','#854F0B')]:
                align = 'left' if col == 'Description' else 'center'
                th_html += f'<th style="padding:10px 14px;text-align:{align};color:#fff;font-weight:600;font-size:11px;letter-spacing:0.04em;background:{bg};">{col}</th>'
            
            rows_html = ''
            # Opening balance row
            rows_html += f'''<tr>
                <td style="padding:10px 14px;text-align:center;border-bottom:0.5px solid #eee;color:#aaa;font-size:11px;">—</td>
                <td style="padding:10px 14px;text-align:left;border-bottom:0.5px solid #eee;font-weight:600;color:#5B4FCF;">Opening Balance (Leela Fund)</td>
                <td style="padding:10px 14px;text-align:center;border-bottom:0.5px solid #eee;">—</td>
                <td style="padding:10px 14px;text-align:center;border-bottom:0.5px solid #eee;font-weight:700;color:#1D6B3B;">₹{leela_total:,.2f}</td>
                <td style="padding:10px 14px;text-align:center;border-bottom:0.5px solid #eee;"><span style="background:#D5F5E3;color:#1D6B3B;font-size:10px;padding:2px 8px;border-radius:12px;font-weight:500;">Received</span></td>
            </tr>'''
            
            running_balance = leela_total
            all_rows = df_leela.reset_index(drop=True)
            
            for i, row in all_rows.iterrows():
                desc = str(row['Description'])
                amt  = row.get('Amount', None)
                has_amt = pd.notna(amt)
                
                if has_amt:
                    running_balance -= float(amt)
                    amt_td      = f'<td style="padding:10px 14px;text-align:center;border-bottom:0.5px solid #eee;color:#A32D2D;font-weight:600;">₹{float(amt):,.2f}</td>'
                    balance_td  = f'<td style="padding:10px 14px;text-align:center;border-bottom:0.5px solid #eee;color:#1D6B3B;font-weight:500;">₹{running_balance:,.2f}</td>'
                    status_td   = '<td style="padding:10px 14px;text-align:center;border-bottom:0.5px solid #eee;"><span style="background:#FCEBEB;color:#A32D2D;font-size:10px;padding:2px 8px;border-radius:12px;font-weight:500;">Spent</span></td>'
                    row_bg      = '#fff'
                else:
                    amt_td      = '<td style="padding:10px 14px;text-align:center;border-bottom:0.5px solid #eee;color:#aaa;">—</td>'
                    balance_td  = '<td style="padding:10px 14px;text-align:center;border-bottom:0.5px solid #eee;color:#aaa;">—</td>'
                    status_td   = '<td style="padding:10px 14px;text-align:center;border-bottom:0.5px solid #eee;"><span style="background:#FFF3CD;color:#856404;font-size:10px;padding:2px 8px;border-radius:12px;font-weight:500;">Pending</span></td>'
                    row_bg      = '#fdfcf5'
                
                rows_html += f'''<tr style="background:{row_bg};">
                    <td style="padding:10px 14px;text-align:center;border-bottom:0.5px solid #eee;color:#aaa;font-size:11px;">{i+1}</td>
                    <td style="padding:10px 14px;text-align:left;border-bottom:0.5px solid #eee;">{desc}</td>
                    {amt_td}{balance_td}{status_td}
                </tr>'''
            
            # Total row
            rows_html += f'''<tr style="background:#f0eaff;font-weight:700;border-top:2px solid #9B59B6;">
                <td colspan="2" style="padding:10px 14px;text-align:left;border-top:2px solid #9B59B6;">Total Utilised</td>
                <td style="padding:10px 14px;text-align:center;border-top:2px solid #9B59B6;color:#A32D2D;">₹{total_spent:,.2f}</td>
                <td style="padding:10px 14px;text-align:center;border-top:2px solid #9B59B6;">—</td>
                <td style="padding:10px 14px;text-align:center;border-top:2px solid #9B59B6;color:#5B4FCF;">{pct_spent:.2f}%</td>
            </tr>
            <tr style="background:linear-gradient(90deg,#eafaf1,#d5f5e3);font-weight:700;">
                <td colspan="2" style="padding:12px 14px;text-align:left;color:#1D6B3B;font-size:14px;border-top:2px solid #27AE60;">💰 Available Balance</td>
                <td style="padding:12px 14px;text-align:center;border-top:2px solid #27AE60;">—</td>
                <td style="padding:12px 14px;text-align:center;border-top:2px solid #27AE60;color:#1D6B3B;font-size:15px;">₹{balance:,.2f}</td>
                <td style="padding:12px 14px;text-align:center;border-top:2px solid #27AE60;color:#1D6B3B;">{pct_left:.2f}% left</td>
            </tr>'''
            
            st.markdown(f"""
            <div style="overflow-x:auto;border-radius:12px;border:0.5px solid #ddd;margin-bottom:1rem;">
            <table style="width:100%;border-collapse:collapse;">
              <thead><tr>{th_html}</tr></thead>
              <tbody>{rows_html}</tbody>
            </table>
            </div>""", unsafe_allow_html=True)
        
    except Exception as e:
        st.warning(f"Leela Fund data not available: {e}")


def render_petty_cash(petty_data, fy_start):
    """Render Petty Cash monthly details for the selected financial year."""
    fy_text = fy_label(fy_start)
    if not petty_data:
        st.info(f"No petty cash data available for **{fy_text}**.")
        return

    month_keys = list(petty_data.keys())
    display_data = enrich_petty_display(petty_data)

    first_month = month_keys[0]
    last_month = month_keys[-1]
    ob_sep = display_data[first_month]["ob"]
    total_cr = sum(display_data[m]["tc"] for m in month_keys)
    total_db = sum(display_data[m]["td"] for m in month_keys)
    overall_cb = display_data[last_month]["cb"]
    month_range = f"{first_month.split()[0]} – {last_month.split()[0]}"

    st.markdown(
        "<div class='sec-header' "
        "style='background:linear-gradient(90deg,#312E81,#6366F1);margin-top:0.5rem;'>"
        f"💵 Petty Cash - Monthly Expense Details ({fy_text})</div>",
        unsafe_allow_html=True,
    )

    st.markdown(f"""
    <div class='metric-row'>
      <div class='metric-card' style='background:linear-gradient(135deg,#312E81,#6366F1);'>
        <div class='metric-label'>Opening Balance ({first_month})</div>
        <div class='metric-value'>-₹{abs(ob_sep):,.0f}</div>
        <div class='metric-sub'>Carried forward from previous period</div>
      </div>
      <div class='metric-card mc-green'>
        <div class='metric-label'>Total Credited ({month_range})</div>
        <div class='metric-value'>₹{total_cr:,.0f}</div>
        <div class='metric-sub'>Across {len(month_keys)} months</div>
      </div>
      <div class='metric-card mc-red'>
        <div class='metric-label'>Total Debited ({month_range})</div>
        <div class='metric-value'>₹{total_db:,.0f}</div>
        <div class='metric-sub'>Across {len(month_keys)} months</div>
      </div>
      <div class='metric-card' style='background:linear-gradient(135deg,#1E3A5F,#2563EB);'>
        <div class='metric-label'>Closing Balance ({last_month})</div>
        <div class='metric-value'>-₹{abs(overall_cb):,.0f}</div>
        <div class='metric-sub'>{ob_sep:,.0f} + {total_cr:,.0f} - {total_db:,.0f} = {overall_cb:,.0f}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<span id="petty-picker-marker"></span>', unsafe_allow_html=True)
        st.markdown(
            "<p style='margin:0 0 12px 0;color:#92400E;font-weight:700;font-size:0.95rem;'>"
            "👇 Choose a month below to view petty cash transactions</p>",
            unsafe_allow_html=True,
        )
        selected_m = st.selectbox("📅 Select Month:", month_keys, key=f"petty_month_sel_{fy_start}")
    md = display_data[selected_m]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Opening Balance", _format_petty_amount(md['ob']))
    c2.metric("Total Credited", f"₹{md['tc']:,.0f}")
    c3.metric("Total Debited", f"₹{md['td']:,.0f}")
    c4.metric("Closing Balance", _format_petty_amount(md['cb']))

    month_colors = {
        "Sep 2025": "#cce5ff", "Oct 2025": "#ffe5cc", "Nov 2025": "#d9ccff",
        "Dec 2025": "#fff0b3", "Jan 2026": "#ffccdd", "Feb 2026": "#b3f0e0",
        "Mar 2026": "#fff3b3", "Apr 2026": "#ccf0cc", "May 2026": "#f0ccff",
        "Jun 2026": "#ffd6cc", "Jul 2026": "#ccf5ff",
    }
    bg = month_colors.get(selected_m, "#ffffff")

    th_html = ""
    for col, bk in [
        ("#", "#312E81"), ("Date", "#374151"), ("Particulars", "#1E40AF"),
        ("To Whom Paid", "#065F46"), ("Vr Type", "#78350F"),
        ("Credit (₹)", "#14532D"), ("Debit (₹)", "#7F1D1D"),
    ]:
        align = "left" if col in ("Particulars", "To Whom Paid", "Date") else "center"
        th_html += (
            f'<th style="padding:8px 10px;text-align:{align};color:#fff;'
            f'font-weight:600;font-size:10px;background:{bk};">{col}</th>'
        )

    rows_html = f"""<tr style="background:#EFF6FF;">
        <td style="padding:7px 10px;text-align:center;color:#9CA3AF;font-size:10px;">-</td>
        <td style="padding:7px 10px;font-size:10.5px;color:#555;"></td>
        <td style="padding:7px 10px;font-weight:600;color:#1E3A5F;">Opening Balance</td>
        <td style="padding:7px 10px;text-align:center;"></td>
        <td style="padding:7px 10px;text-align:center;"></td>
        <td style="padding:7px 10px;text-align:right;">-</td>
        <td style="padding:7px 10px;text-align:right;font-weight:600;color:#DC2626;">{_format_petty_amount(md["ob"])}</td>
    </tr>"""

    for row in md["rows"]:
        sr, date, part, whom, vr_type, cr, db = row
        cr_v = float(cr) if cr not in ("", None) else 0
        db_v = float(db) if db not in ("", None) else 0
        vr_badge = (
            '<span style="background:#FFF3CD;color:#856404;font-size:9px;padding:1px 5px;border-radius:8px;">Cash</span>'
            if str(vr_type).lower().strip() == "cash"
            else '<span style="background:#DBEAFE;color:#1E40AF;font-size:9px;padding:1px 5px;border-radius:8px;">Online</span>'
            if vr_type
            else ""
        )
        cr_td = (
            f'<td style="padding:7px 10px;text-align:right;color:#15803D;font-weight:600;">₹{cr_v:,.0f}</td>'
            if cr_v
            else '<td style="padding:7px 10px;text-align:right;color:#aaa;">-</td>'
        )
        db_td = (
            f'<td style="padding:7px 10px;text-align:right;color:#DC2626;font-weight:600;">₹{db_v:,.0f}</td>'
            if db_v
            else '<td style="padding:7px 10px;text-align:right;color:#aaa;">-</td>'
        )
        rows_html += f"""<tr style="background:{bg};border-bottom:0.5px solid #e5e7eb;">
            <td style="padding:7px 10px;text-align:center;color:#9CA3AF;font-size:10px;">{sr}</td>
            <td style="padding:7px 10px;font-size:10.5px;color:#6B7280;">{date}</td>
            <td style="padding:7px 10px;text-align:left;">{part}</td>
            <td style="padding:7px 10px;text-align:center;font-size:10.5px;">{whom}</td>
            <td style="padding:7px 10px;text-align:center;">{vr_badge}</td>
            {cr_td}{db_td}
        </tr>"""

    rows_html += f"""<tr style="background:#F3F4F6;font-weight:700;border-top:2px solid #6366F1;">
        <td colspan="5" style="padding:8px 10px;text-align:right;color:#6B7280;font-size:11px;">TOTAL</td>
        <td style="padding:8px 10px;text-align:right;color:#15803D;">₹{md["tc"]:,.0f}</td>
        <td style="padding:8px 10px;text-align:right;color:#DC2626;">₹{md["td"]:,.0f}</td>
    </tr>
    <tr style="background:#FFFBEB;font-weight:700;border-top:2px solid #D97706;">
        <td colspan="5" style="padding:8px 10px;text-align:right;font-size:11px;">CLOSING BALANCE</td>
        <td colspan="2" style="padding:8px 10px;text-align:center;font-size:13px;color:#DC2626;">{_format_petty_amount(md["cb"])}</td>
    </tr>"""

    st.markdown(
        f"""<div style="overflow-x:auto;border-radius:10px;border:0.5px solid #ddd;margin-top:.5rem;">
    <table style="width:100%;border-collapse:collapse;font-size:11.5px;">
      <thead><tr>{th_html}</tr></thead>
      <tbody>{rows_html}</tbody>
    </table></div>""",
        unsafe_allow_html=True,
    )


def main():
    st.markdown('<h1 class="main-header">🏢 Zen Estate Financial Dashboard</h1>', unsafe_allow_html=True)

    if "petty_cache_bust" not in st.session_state:
        st.session_state.petty_cache_bust = 0

    with st.spinner('Loading latest data from repository...'):
        df_monthly_all, df_wings_all, df_vendors_all, df_extra_all, df_fines_all = load_excel_from_github()
        petty_by_fy = load_petty_cash_data(st.session_state.petty_cache_bust)
        df_leela = load_leela_data()

    available_fys = get_available_financial_years(petty_by_fy, df_monthly_all)
    fy_options = {fy_label(fy): fy for fy in available_fys}

    with st.container(border=True):
        st.markdown('<span id="fy-picker-marker"></span>', unsafe_allow_html=True)
        st.markdown(
            "<div class='fy-panel-banner'>📅 Select Financial Year</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='margin:14px 0 10px 0;color:#1E3A8A;font-weight:800;font-size:1rem;"
            "letter-spacing:0.02em;'>Choose the year to view all dashboard sections</p>",
            unsafe_allow_html=True,
        )
        selected_fy_label = st.selectbox(
            "Financial Year:",
            list(fy_options.keys()),
            key="fy_selector",
            label_visibility="visible",
        )

    selected_fy = fy_options[selected_fy_label]
    st.markdown(
        f"<div class='fy-active-badge'>✓ &nbsp;Showing data for &nbsp; <span style='font-size:1.05rem;'>"
        f"{selected_fy_label}</span></div>",
        unsafe_allow_html=True,
    )

    df_monthly = filter_df_by_fy(df_monthly_all, selected_fy)
    df_wings = filter_df_by_fy(df_wings_all, selected_fy)
    df_vendors = filter_df_by_fy(df_vendors_all, selected_fy)
    df_extra_income_breakdown = filter_df_by_fy(df_extra_all, selected_fy)
    df_fines = filter_df_by_fy(df_fines_all, selected_fy)
    petty_data = filter_petty_by_fy(petty_by_fy, selected_fy)

    tab_overview, tab_leela, tab_petty, tab_extra, tab_wings, tab_downloads = st.tabs([
        "📊 Overview",
        "🏦 Leela Fund",
        "💵 Petty Cash",
        "💰 Extra Income",
        "🏢 Wings & Shops",
        "📥 Downloads",
    ])

    with tab_overview:
        if df_monthly.empty:
            st.info(f"No main collection/expense data available for **{selected_fy_label}**.")
        else:
            # Portfolio metric cards
            st.markdown("<div class='sec-header sec-blue'>📊 Portfolio Overview</div>", unsafe_allow_html=True)
            total_to_be   = df_monthly['To_Be'].sum()
            total_received = df_monthly['Received'].sum()
            total_fines_sum = df_fines['Total_Fine'].sum() if not df_fines.empty else 0
            total_extra   = df_monthly['Extra_Income'].sum()
            collection_pct = (total_received / total_to_be * 100) if total_to_be > 0 else 0
            st.markdown(f"""
                <div class='metric-row'>
                  <div class='metric-card mc-blue'>
                    <div class='metric-label'>Total to be received</div>
                    <div class='metric-value'>₹{total_to_be/10000000:.2f} Cr</div>
                    <div class='metric-sub'>{selected_fy_label}</div>
                  </div>
                  <div class='metric-card mc-green'>
                    <div class='metric-label'>Total received</div>
                    <div class='metric-value'>₹{total_received/10000000:.2f} Cr</div>
                    <div class='metric-sub'>{collection_pct:.1f}% collection rate</div>
                  </div>
                  <div class='metric-card mc-amber'>
                    <div class='metric-label'>Total fines levied</div>
                    <div class='metric-value'>₹{total_fines_sum:,.0f}</div>
                    <div class='metric-sub'>Across all wings/shops</div>
                  </div>
                  <div class='metric-card mc-red'>
                    <div class='metric-label'>Total extra income</div>
                    <div class='metric-value'>₹{total_extra:,.0f}</div>
                    <div class='metric-sub'>NBH, Events, Lift, Scrap etc.</div>
                  </div>
                </div>
            """, unsafe_allow_html=True)
            # Monthly Overview Table
            st.markdown("""
                <div class='sec-header sec-blue'>📊 Monthly Overview — To Be vs Received</div>
            """, unsafe_allow_html=True)
            
            overview_data = df_monthly.copy()
            overview_data = overview_data.rename(columns={'To_Be':'To Be Received','Received':'Actual Received','Extra_Income':'Extra Income'})
            overview_data['Difference'] = overview_data['To Be Received'] - overview_data['Actual Received']
            
            # Build fine details per month
            fine_by_month = {}
            if not df_fines.empty:
                for month in overview_data['Month'].unique():
                    mfines = df_fines[df_fines['Month'] == month]
                    parts = []
                    for _, fr in mfines.iterrows():
                        wing = fr['Wing']
                        if fr['HK'] > 0:       parts.append(f"{wing}·HK ₹{fr['HK']:,.0f}")
                        if fr['Quinteze'] > 0:  parts.append(f"{wing}·Q ₹{fr['Quinteze']:,.0f}")
                        if fr['Security'] > 0:  parts.append(f"{wing}·Sec ₹{fr['Security']:,.0f}")
                        if fr['STP'] > 0:       parts.append(f"{wing}·STP ₹{fr['STP']:,.0f}")
                    fine_by_month[month] = parts
            
            # Build HTML table manually to support fine detail tags
            month_colors = {
                'Sep':'#cce5ff','Oct':'#ffe5cc','Nov':'#d9ccff','Dec':'#fff0b3',
                'Jan':'#ffccdd','Feb':'#b3f0e0','Mar':'#fff3b3','Apr':'#ccf0cc','May':'#f0ccff'
            }
            header_cols = {
                'Month':       '#555555',
                'To Be Received': '#185FA5',
                'Actual Received':'#1D9E75',
                'Difference':  '#A32D2D',
                'Expense':     '#BA7517',
                'Extra Income':'#D4537E',
                'Fine Details':'#D85A30',
            }
            th_html = '<th style="padding:10px 12px;color:#fff;font-weight:600;font-size:11px;background:#555;"></th>'
            for col, bg in header_cols.items():
                th_html += f'<th style="padding:10px 12px;text-align:center;color:#fff;font-weight:600;font-size:11px;letter-spacing:0.03em;background:{bg};">{col}</th>'
            
            rows_html = ''
            for i, row in overview_data.iterrows():
                month = row['Month']
                bg = month_colors.get(month, '#ffffff')
                td_style = f'padding:9px 12px;text-align:center;background:{bg};border-bottom:0.5px solid #ddd;font-size:12px;'
                
                diff = row['Difference']
                if diff > 0:
                    diff_style = td_style + 'color:#8b0000;font-weight:700;'
                elif diff < 0:
                    diff_style = td_style + 'color:#3B6D11;font-weight:700;'
                else:
                    diff_style = td_style + 'color:#555;'
                
                # Fine detail tags
                fines = fine_by_month.get(month, [])
                if fines:
                    tags = ''.join([f'<span style="display:inline-flex;font-size:10px;background:#FAEEDA;color:#854F0B;padding:2px 7px;border-radius:4px;margin:2px;font-weight:500;white-space:nowrap;border:0.5px solid #e0b870;">{f}</span>' for f in fines])
                    fine_td = f'<td style="{td_style}text-align:left;">{tags}</td>'
                else:
                    fine_td = f'<td style="{td_style}color:#bbb;">—</td>'
                
                rows_html += f'''<tr>
                    <td style="{td_style}color:#999;font-size:11px;">{i}</td>
                    <td style="{td_style}font-weight:500;">{month}</td>
                    <td style="{td_style}">₹{row["To Be Received"]:,.2f}</td>
                    <td style="{td_style}">₹{row["Actual Received"]:,.2f}</td>
                    <td style="{diff_style}">₹{diff:,.2f}</td>
                    <td style="{td_style}">₹{row["Expense"]:,.2f}</td>
                    <td style="{td_style}">₹{row["Extra Income"]:,.2f}</td>
                    {fine_td}
                </tr>'''
            
            st.markdown(f"""
            <div style="overflow-x:auto;border-radius:10px;border:1px solid #ddd;margin-bottom:1rem;">
            <table style="width:100%;border-collapse:collapse;">
              <thead><tr>{th_html}</tr></thead>
              <tbody>{rows_html}</tbody>
            </table>
            </div>""", unsafe_allow_html=True)

    with tab_leela:
        render_leela_fund(df_leela)

    with tab_petty:
        refresh_col, info_col = st.columns([1, 3])
        with refresh_col:
            if st.button(
                "🔄 Refresh petty cash data",
                key="refresh_petty_btn",
                help="Use after uploading an updated Petty_Cash_Expense_Details.xlsx to GitHub",
            ):
                load_petty_cash_data.clear()
                st.session_state.petty_cache_bust += 1
                st.rerun()
        with info_col:
            st.caption(
                "Petty cash loads from GitHub (`Petty_Cash_Expense_Details.xlsx`). "
                "After updating the file on GitHub, click **Refresh** here — "
                "the dashboard does not auto-detect Excel changes."
            )
        render_petty_cash(petty_data, selected_fy)

    with tab_extra:
        if df_monthly.empty:
            st.info(f"No extra income data for **{selected_fy_label}**.")
        else:
            # Extra Income
            st.markdown("""
                <div class='sec-header sec-purple'>💰 Extra Income — Month-wise</div>
            """, unsafe_allow_html=True)
            fig2 = create_extra_income_chart(df_monthly)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True)
            
            # Extra Income Breakdown by Source
            if not df_extra_income_breakdown.empty:
                st.markdown("""
                    <div class='sec-header sec-pink'>📋 Extra Income Breakdown</div>
                """, unsafe_allow_html=True)
                
                # Create a formatted dataframe
                breakdown_display = df_extra_income_breakdown.copy()
                
                # Add total column (all 6 income sources)
                breakdown_display['Total'] = breakdown_display[['NBH', 'Lift', 'Event', 'Scrap', 'Parking_Fine', 'ClubHouse_Booking & Gym']].sum(axis=1)
                
                render_html_table(
                    breakdown_display,
                    fmt={'NBH':'₹{:,.2f}','Lift':'₹{:,.2f}','Event':'₹{:,.2f}','Scrap':'₹{:,.2f}',
                         'Parking_Fine':'₹{:,.2f}','ClubHouse_Booking & Gym':'₹{:,.2f}','Total':'₹{:,.2f}'}
                )
            
    with tab_wings:
        if df_wings.empty:
            st.info(f"No wing/shop data for **{selected_fy_label}**.")
        else:
            # Wing/Shop Filter Section
            st.markdown("<div class='sec-header sec-orange'>🏢 Wing / Shop-Wise Analysis</div>", unsafe_allow_html=True)
            all_wings_shops = sorted(df_wings['Wing'].unique())

            if all_wings_shops:
                col1, col2 = st.columns([1, 3])

                with col1:
                    selected_wing_shop = st.selectbox(
                        'Select a Wing/Shop:', all_wings_shops, key=f'wing_shop_filter_{selected_fy}'
                    )

                with col2:
                    st.write("")

                wing_shop_data = df_wings[df_wings['Wing'] == selected_wing_shop].copy()

                if not wing_shop_data.empty:
                    total_to_be = wing_shop_data['To_Be'].sum()
                    total_received = wing_shop_data['Received'].sum()
                    total_difference = wing_shop_data['Difference'].sum()

                    wing_shop_fines = pd.DataFrame()
                    total_fines = 0
                    if not df_fines.empty:
                        wing_shop_fines = df_fines[df_fines['Wing'] == selected_wing_shop].copy()
                        if not wing_shop_fines.empty:
                            total_fines = wing_shop_fines['Total_Fine'].sum()

                    st.subheader(f"📊 {selected_wing_shop} - Summary")
                    metric_cols = st.columns(4)

                    with metric_cols[0]:
                        st.metric("Total To Be Received", f"₹{total_to_be:,.2f}")
                    with metric_cols[1]:
                        st.metric("Total Received", f"₹{total_received:,.2f}")
                    with metric_cols[2]:
                        st.metric("Total Fines Deducted", f"₹{total_fines:,.2f}")

                    adjusted_difference = total_difference - total_fines
                    with metric_cols[3]:
                        if adjusted_difference > 0:
                            st.metric("Total Pending", f"₹{adjusted_difference:,.2f}", delta=None,
                                     help="Amount still to be received after fines")
                        else:
                            st.metric("Total Excess", f"₹{abs(adjusted_difference):,.2f}", delta=None,
                                     help="Amount received extra after fines")

                    st.subheader(f"📋 {selected_wing_shop} - Monthly Breakdown")
                    wing_shop_display = wing_shop_data.copy()
                    if 'Wing' in wing_shop_display.columns:
                        wing_shop_display = wing_shop_display.drop('Wing', axis=1)
                    month_order = {'Sep': 1, 'Oct': 2, 'Nov': 3, 'Dec': 4, 'Jan': 5, 'Feb': 6,
                                   'Mar': 7, 'Apr': 8, 'May': 9, 'Jun': 10, 'Jul': 11}
                    wing_shop_display['month_sort'] = wing_shop_display['Month'].map(month_order)
                    wing_shop_display = wing_shop_display.sort_values('month_sort').drop('month_sort', axis=1)
                    wing_shop_display = wing_shop_display.rename(columns={
                        'To_Be': 'To Be Received',
                        'Received': 'Actual Received',
                        'Difference': 'Pending/Excess (-ve = Excess)'
                    })

                    wing_shop_display['Fine_Details'] = '-'
                    wing_shop_display['Fine_Amount'] = 0.0

                    if not wing_shop_fines.empty:
                        for idx, row in wing_shop_display.iterrows():
                            month = row['Month']
                            fine_month_data = wing_shop_fines[wing_shop_fines['Month'] == month]
                            if not fine_month_data.empty:
                                fine_row = fine_month_data.iloc[0]
                                hk = float(fine_row['HK']) if pd.notna(fine_row['HK']) else 0
                                quinteze = float(fine_row['Quinteze']) if pd.notna(fine_row['Quinteze']) else 0
                                security = float(fine_row['Security']) if pd.notna(fine_row['Security']) else 0
                                stp = float(fine_row['STP']) if pd.notna(fine_row['STP']) else 0
                                total_month_fine = hk + quinteze + security + stp
                                fine_details_list = []
                                if hk > 0:
                                    fine_details_list.append(f"HK: ₹{hk:,.0f}")
                                if quinteze > 0:
                                    fine_details_list.append(f"Q: ₹{quinteze:,.0f}")
                                if security > 0:
                                    fine_details_list.append(f"Sec: ₹{security:,.0f}")
                                if stp > 0:
                                    fine_details_list.append(f"STP: ₹{stp:,.0f}")
                                if fine_details_list:
                                    wing_shop_display.at[idx, 'Fine_Details'] = ' | '.join(fine_details_list)
                                    wing_shop_display.at[idx, 'Fine_Amount'] = total_month_fine

                    wing_shop_display['Pending/Excess (-ve = Excess)'] = (
                        wing_shop_display['Pending/Excess (-ve = Excess)'] - wing_shop_display['Fine_Amount']
                    )
                    render_html_table(
                        wing_shop_display[['Month', 'To Be Received', 'Actual Received', 'Fine_Details', 'Pending/Excess (-ve = Excess)']],
                        fmt={'To Be Received':'₹{:,.2f}', 'Actual Received':'₹{:,.2f}', 'Pending/Excess (-ve = Excess)':'₹{:,.2f}'}
                    )
                else:
                    st.warning(f"No data available for {selected_wing_shop}")

            st.markdown("<div class='sec-header sec-teal'>📋 Wing / Shop Monthly Details — All</div>", unsafe_allow_html=True)
            st.markdown("**Monthly breakdown showing To Be Received, Actual Received, and Difference for each Wing/Shop** *(Sorted by Month)*")
            detailed_breakdown = df_wings.copy()
            detailed_breakdown = detailed_breakdown[~detailed_breakdown['Wing'].isin(['C Shop Rahul', 'C Shop Sagar'])]

            if not df_fines.empty:
                fine_summary = df_fines[['Month', 'Wing', 'HK', 'Quinteze', 'Security', 'STP', 'Total_Fine']].copy()

                def format_fine_detail(row):
                    parts = []
                    if row['HK'] > 0:
                        parts.append(f"HK:₹{row['HK']:,.0f}")
                    if row['Quinteze'] > 0:
                        parts.append(f"Q:₹{row['Quinteze']:,.0f}")
                    if row['Security'] > 0:
                        parts.append(f"Sec:₹{row['Security']:,.0f}")
                    if row['STP'] > 0:
                        parts.append(f"STP:₹{row['STP']:,.0f}")
                    return ' | '.join(parts) if parts else '-'

                fine_summary['Fine_Details'] = fine_summary.apply(format_fine_detail, axis=1)
                fine_summary['Fine_Amount'] = fine_summary['Total_Fine']
                detailed_breakdown = detailed_breakdown.merge(
                    fine_summary[['Month', 'Wing', 'Fine_Details', 'Fine_Amount']],
                    on=['Month', 'Wing'], how='left'
                )
                detailed_breakdown['Fine_Details'] = detailed_breakdown['Fine_Details'].fillna('-')
                detailed_breakdown['Fine_Amount'] = detailed_breakdown['Fine_Amount'].fillna(0)
            else:
                detailed_breakdown['Fine_Details'] = '-'
                detailed_breakdown['Fine_Amount'] = 0

            month_order = {'Sep': 1, 'Oct': 2, 'Nov': 3, 'Dec': 4, 'Jan': 5, 'Feb': 6,
                           'Mar': 7, 'Apr': 8, 'May': 9, 'Jun': 10, 'Jul': 11}
            detailed_breakdown['Month_Sort'] = detailed_breakdown['Month'].map(month_order)
            detailed_breakdown = detailed_breakdown.sort_values(['Month_Sort', 'Wing']).drop('Month_Sort', axis=1)
            detailed_breakdown = detailed_breakdown.reset_index(drop=True)
            detailed_breakdown = detailed_breakdown.rename(columns={
                'To_Be': 'To Be Received',
                'Received': 'Actual Received'
            })
            render_html_table(
                detailed_breakdown[['Wing', 'Month', 'To Be Received', 'Actual Received', 'Fine_Details', 'Difference']],
                fmt={'To Be Received':'₹{:,.2f}', 'Actual Received':'₹{:,.2f}', 'Difference':'₹{:,.2f}'}
            )
            
    with tab_downloads:
        st.markdown("### 📥 Download Reports")
        if df_monthly.empty and df_wings.empty:
            st.info(f"No CSV reports available for **{selected_fy_label}**.")
        else:
            col1, col2, col3 = st.columns(3)

            with col1:
                if not df_monthly.empty:
                    csv_monthly = df_monthly.to_csv(index=False)
                    st.download_button(
                        "📊 Monthly Summary (CSV)",
                        csv_monthly,
                        f"monthly_summary_{selected_fy}_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv",
                        key="dl_monthly",
                    )

            with col2:
                if not df_wings.empty:
                    csv_wings = df_wings.to_csv(index=False)
                    st.download_button(
                        "🏘️ Wing Data (CSV)",
                        csv_wings,
                        f"wing_data_{selected_fy}_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv",
                        key="dl_wings",
                    )

            with col3:
                if not df_vendors.empty:
                    csv_vendors = df_vendors.to_csv(index=False)
                    st.download_button(
                        "💼 Vendor Data (CSV)",
                        csv_vendors,
                        f"vendor_data_{selected_fy}_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv",
                        key="dl_vendors",
                    )

    if df_monthly_all.empty and not petty_by_fy:
        st.error("❌ Unable to load data from repository")
        st.info("Please ensure the Excel files are committed to the GitHub repository.")

if __name__ == "__main__":
    main()
