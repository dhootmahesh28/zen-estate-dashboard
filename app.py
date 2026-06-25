import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Zen Estate Financial Dashboard",
    page_icon="🏢",
    layout="wide"
)

st.markdown("""
    <style>
    /* ── Page background ── */
    .stApp { background: #f4f6fa; }

    /* ── Main title ── */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        padding: 1.2rem 1.5rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        margin-bottom: 1.5rem;
        letter-spacing: 0.02em;
        text-shadow: 0 2px 8px rgba(0,0,0,0.8);
        -webkit-text-fill-color: #ffffff;
    }

    /* ── Section headers ── */
    .sec-header {
        color: white;
        padding: 11px 18px;
        border-radius: 12px;
        font-size: 1.05rem;
        font-weight: 600;
        margin: 1.2rem 0 0.7rem 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .sec-blue   { background: linear-gradient(90deg, #185FA5, #378ADD); }
    .sec-green  { background: linear-gradient(90deg, #3B6D11, #639922); }
    .sec-purple { background: linear-gradient(90deg, #3C3489, #7F77DD); }
    .sec-orange { background: linear-gradient(90deg, #993C1D, #D85A30); }
    .sec-pink   { background: linear-gradient(90deg, #993556, #D4537E); }
    .sec-teal   { background: linear-gradient(90deg, #0F6E56, #1D9E75); }

    /* ── Metric cards ── */
    .metric-row { display: flex; gap: 12px; margin-bottom: 1rem; }
    .metric-card {
        flex: 1;
        border-radius: 12px;
        padding: 14px 16px;
        color: white;
        min-width: 0;
    }
    .mc-blue   { background: linear-gradient(135deg, #185FA5, #378ADD); }
    .mc-green  { background: linear-gradient(135deg, #3B6D11, #639922); }
    .mc-amber  { background: linear-gradient(135deg, #854F0B, #BA7517); }
    .mc-red    { background: linear-gradient(135deg, #A32D2D, #E24B4A); }
    .metric-label { font-size: 0.7rem; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px; }
    .metric-value { font-size: 1.35rem; font-weight: 600; }
    .metric-sub   { font-size: 0.68rem; opacity: 0.75; margin-top: 3px; }

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
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=0)
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

@st.cache_data(ttl=0)
def load_leela_data():
    """Load Leela Fund expenditure data from Sheet3."""
    try:
        url = "https://raw.githubusercontent.com/dhootmahesh28/zen-estate-dashboard/master/Zen_Estate_Combined_Expenses_Q1.xlsx"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        df = pd.read_excel(io.BytesIO(response.content), sheet_name='Sheet3', header=None)
        
        items = []
        for row in range(df.shape[0]):
            desc = df.iloc[row, 1]
            amt  = df.iloc[row, 2] if df.shape[1] > 2 else None
            if pd.notna(desc) and isinstance(desc, str) and desc.strip():
                items.append({
                    'Description': desc.strip(),
                    'Amount': float(amt) if pd.notna(amt) and isinstance(amt, (int, float)) else None
                })
        return pd.DataFrame(items)
    except Exception as e:
        return pd.DataFrame()
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
            {'name': 'May', 'to_be_row': 147, 'received_row': 146, 'diff_row': 148, 'summary_row': 152, 'expense_col': 15}
        ]
        
        # Monthly summary data
        monthly_data = []
        wing_data = []
        
        for month_info in months_info:
            month = month_info['name']
            
            # Get summary totals
            to_be = df.iloc[month_info['summary_row'], 6] if pd.notna(df.iloc[month_info['summary_row'], 6]) else 0
            received = df.iloc[month_info['summary_row'], 9] if pd.notna(df.iloc[month_info['summary_row'], 9]) else 0
            expense = df.iloc[month_info['summary_row'], month_info['expense_col']] if pd.notna(df.iloc[month_info['summary_row'], month_info['expense_col']]) else 0
            extra_income = df.iloc[month_info['summary_row'], 18] if pd.notna(df.iloc[month_info['summary_row'], 18]) else 0
            
            monthly_data.append({
                'Month': month,
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
                            'Month': section['month']
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
            'May': 146   # Total row for May
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
            {'month': 'May', 'vendor_row': 138}
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
                            fine_data[key] = {'Month': month, 'Wing': wing, 'HK': 0, 'Quinteze': 0, 'Security': 0, 'STP': 0}
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
    year = "2026" if month in ["Jan", "Feb", "Mar", "Apr", "May"] else "2025"
    
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
    'Jan': '#ffccdd', 'Feb': '#b3f0e0', 'Mar': '#fff3b3', 'Apr': '#ccf0cc', 'May': '#f0ccff',
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


def main():
    st.markdown('<h1 class="main-header">🏢 Zen Estate Financial Dashboard (Sep 2025 – May 2026)</h1>', unsafe_allow_html=True)
    
    # Auto-load data from GitHub (no upload needed)
    with st.spinner('Loading latest data from repository...'):
        df_monthly, df_wings, df_vendors, df_extra_income_breakdown, df_fines = load_excel_from_github()
    
    if not df_monthly.empty:
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
                    <div class='metric-sub'>Sep 2025 – May 2026</div>
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
            
            st.markdown("---")
            
            # Vendor Breakdown - 5 separate charts for each month
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
            
            # Wing/Shop Filter Section
            st.markdown("<div class='sec-header sec-orange'>🏢 Wing / Shop-Wise Analysis</div>", unsafe_allow_html=True)
            
            if not df_wings.empty:
                # Get unique wings and shops - sorted
                all_wings_shops = sorted(df_wings['Wing'].unique())
                
                if all_wings_shops:
                    # Create columns for better layout
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        selected_wing_shop = st.selectbox('Select a Wing/Shop:', all_wings_shops, key='wing_shop_filter')
                    
                    with col2:
                        st.write("")  # Spacing
                    
                    # Filter data for selected wing/shop
                    wing_shop_data = df_wings[df_wings['Wing'] == selected_wing_shop].copy()
                    
                    if not wing_shop_data.empty:
                        # Calculate totals
                        total_to_be = wing_shop_data['To_Be'].sum()
                        total_received = wing_shop_data['Received'].sum()
                        total_difference = wing_shop_data['Difference'].sum()
                        
                        # Get fine data for selected wing/shop
                        wing_shop_fines = pd.DataFrame()
                        total_fines = 0
                        if not df_fines.empty:
                            wing_shop_fines = df_fines[df_fines['Wing'] == selected_wing_shop].copy()
                            if not wing_shop_fines.empty:
                                total_fines = wing_shop_fines['Total_Fine'].sum()
                        
                        # Display metrics
                        st.subheader(f"📊 {selected_wing_shop} - Summary")
                        
                        metric_cols = st.columns(4)
                        
                        with metric_cols[0]:
                            st.metric("Total To Be Received", f"₹{total_to_be:,.2f}")
                        
                        with metric_cols[1]:
                            st.metric("Total Received", f"₹{total_received:,.2f}")
                        
                        with metric_cols[2]:
                            st.metric("Total Fines Deducted", f"₹{total_fines:,.2f}")
                        
                        # Calculate adjusted difference (pending - fines)
                        adjusted_difference = total_difference - total_fines
                        
                        with metric_cols[3]:
                            # Color code based on pending/excess (after deducting fines)
                            if adjusted_difference > 0:
                                st.metric("Total Pending", f"₹{adjusted_difference:,.2f}", delta=None, 
                                         help="Amount still to be received after fines")
                            else:
                                st.metric("Total Excess", f"₹{abs(adjusted_difference):,.2f}", delta=None,
                                         help="Amount received extra after fines")
                        
                        # Display detailed breakdown
                        st.subheader(f"📋 {selected_wing_shop} - Monthly Breakdown")
                        
                        wing_shop_display = wing_shop_data.copy()
                        # Drop Wing column - not needed in per-wing breakdown table
                        if 'Wing' in wing_shop_display.columns:
                            wing_shop_display = wing_shop_display.drop('Wing', axis=1)
                        # Sort by month chronologically (Sep, Oct, Nov, Dec, Jan)
                        month_order = {'Sep': 1, 'Oct': 2, 'Nov': 3, 'Dec': 4, 'Jan': 5, 'Feb': 6, 'Mar': 7, 'Apr': 8, 'May': 9}
                        wing_shop_display['month_sort'] = wing_shop_display['Month'].map(month_order)
                        wing_shop_display = wing_shop_display.sort_values('month_sort')
                        wing_shop_display = wing_shop_display.drop('month_sort', axis=1)
                        
                        wing_shop_display = wing_shop_display.rename(columns={
                            'To_Be': 'To Be Received',
                            'Received': 'Actual Received',
                            'Difference': 'Pending/Excess (-ve = Excess)'
                        })
                        
                        # Add Fine_Details column (only if this is a Wing with fine data)
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
                        
                        # Calculate adjusted pending/excess after deducting fines
                        wing_shop_display['Pending/Excess (-ve = Excess)'] = wing_shop_display['Pending/Excess (-ve = Excess)'] - wing_shop_display['Fine_Amount']
                        
                        render_html_table(
                            wing_shop_display[['Month', 'To Be Received', 'Actual Received', 'Fine_Details', 'Pending/Excess (-ve = Excess)']],
                            fmt={'To Be Received':'₹{:,.2f}', 'Actual Received':'₹{:,.2f}', 'Pending/Excess (-ve = Excess)':'₹{:,.2f}'}
                        )
                    else:
                        st.warning(f"No data available for {selected_wing_shop}")
            
            # Detailed Wing/Shop Monthly Breakdown Table
            st.markdown("<div class='sec-header sec-teal'>📋 Wing / Shop Monthly Details — All</div>", unsafe_allow_html=True)
            if not df_wings.empty:
                st.markdown("**Monthly breakdown showing To Be Received, Actual Received, and Difference for each Wing/Shop** *(Sorted by Month)*")
                
                # Format the dataframe for better display
                detailed_breakdown = df_wings.copy()
                
                # Remove C Shop Rahul and C Shop Sagar (no data)
                detailed_breakdown = detailed_breakdown[~detailed_breakdown['Wing'].isin(['C Shop Rahul', 'C Shop Sagar'])]
                
                # Merge fine data into detailed breakdown
                if not df_fines.empty:
                    # Build a fine summary per (Wing, Month)
                    fine_summary = df_fines[['Month', 'Wing', 'HK', 'Quinteze', 'Security', 'STP', 'Total_Fine']].copy()
                    
                    def format_fine_detail(row):
                        parts = []
                        if row['HK'] > 0:       parts.append(f"HK:₹{row['HK']:,.0f}")
                        if row['Quinteze'] > 0:  parts.append(f"Q:₹{row['Quinteze']:,.0f}")
                        if row['Security'] > 0:  parts.append(f"Sec:₹{row['Security']:,.0f}")
                        if row['STP'] > 0:       parts.append(f"STP:₹{row['STP']:,.0f}")
                        return ' | '.join(parts) if parts else '-'
                    
                    fine_summary['Fine_Details'] = fine_summary.apply(format_fine_detail, axis=1)
                    fine_summary['Fine_Amount']  = fine_summary['Total_Fine']
                    detailed_breakdown = detailed_breakdown.merge(
                        fine_summary[['Month', 'Wing', 'Fine_Details', 'Fine_Amount']],
                        on=['Month', 'Wing'], how='left'
                    )
                    detailed_breakdown['Fine_Details'] = detailed_breakdown['Fine_Details'].fillna('-')
                    detailed_breakdown['Fine_Amount']  = detailed_breakdown['Fine_Amount'].fillna(0)
                else:
                    detailed_breakdown['Fine_Details'] = '-'
                    detailed_breakdown['Fine_Amount']  = 0
                
                # Create a custom sort order for months
                month_order = {'Sep': 1, 'Oct': 2, 'Nov': 3, 'Dec': 4, 'Jan': 5, 'Feb': 6, 'Mar': 7, 'Apr': 8, 'May': 9}
                detailed_breakdown['Month_Sort'] = detailed_breakdown['Month'].map(month_order)
                
                # Sort by Month FIRST (chronologically), then Wing (alphabetically)
                # This groups all Wings/Shops for each month together
                detailed_breakdown = detailed_breakdown.sort_values(['Month_Sort', 'Wing'])
                
                # Remove the helper column
                detailed_breakdown = detailed_breakdown.drop('Month_Sort', axis=1)
                
                # Reset index to show sequential numbering starting from 0
                detailed_breakdown = detailed_breakdown.reset_index(drop=True)
                
                # Rename columns for clarity
                detailed_breakdown = detailed_breakdown.rename(columns={
                    'To_Be': 'To Be Received',
                    'Received': 'Actual Received'
                })
                
                render_html_table(
                    detailed_breakdown[['Wing', 'Month', 'To Be Received', 'Actual Received', 'Fine_Details', 'Difference']],
                    fmt={'To Be Received':'₹{:,.2f}', 'Actual Received':'₹{:,.2f}', 'Difference':'₹{:,.2f}'}
                )
            
            # Download Reports
            st.markdown("---")
            st.markdown("### 📥 Download Reports")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv_monthly = df_monthly.to_csv(index=False)
                st.download_button(
                    "📊 Monthly Summary (CSV)",
                    csv_monthly,
                    f"monthly_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
            
            with col2:
                csv_wings = df_wings.to_csv(index=False)
                st.download_button(
                    "🏘️ Wing Data (CSV)",
                    csv_wings,
                    f"wing_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
            
            with col3:
                if not df_vendors.empty:
                    csv_vendors = df_vendors.to_csv(index=False)
                    st.download_button(
                        "💼 Vendor Data (CSV)",
                        csv_vendors,
                        f"vendor_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
    # ── LEELA FUND DETAILS ──────────────────────────────────────────────────────
    st.markdown("<div class='sec-header' style='background:linear-gradient(90deg,#5B4FCF,#9B59B6);margin-top:1.5rem;'>🏦 Leela Fund Details</div>", unsafe_allow_html=True)
    
    try:
        df_leela = load_leela_data()
        
        if not df_leela.empty:
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
    
    # ── END LEELA FUND ───────────────────────────────────────────────────────────

    else:
        st.warning("⚠️ No data found")
    
    # Error handling if data couldn't be loaded
    if df_monthly.empty:
        st.error("❌ Unable to load data from repository")
        st.info("Please ensure the Excel file is committed to the GitHub repository.")

if __name__ == "__main__":
    main()
