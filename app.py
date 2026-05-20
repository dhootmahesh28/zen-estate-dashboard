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
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    /* Center align all dataframe cells and headers - Multiple selectors for better compatibility */
    div[data-testid="stDataFrame"] table th,
    div[data-testid="stDataFrame"] thead th,
    .dataframe th,
    .dataframe thead th {
        text-align: center !important;
        background-color: #1f77b4 !important;
        color: white !important;
        font-weight: bold !important;
        padding: 12px !important;
        font-size: 1.1rem !important;
    }
    div[data-testid="stDataFrame"] table td,
    div[data-testid="stDataFrame"] tbody td,
    .dataframe td,
    .dataframe tbody td {
        text-align: center !important;
        padding: 10px !important;
        font-size: 1rem !important;
    }
    /* Also target the styled dataframes */
    .row_heading {
        text-align: center !important;
    }
    .col_heading {
        text-align: center !important;
        background-color: #1f77b4 !important;
        color: white !important;
    }
    .data {
        text-align: center !important;
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
            {'name': 'Apr', 'to_be_row': 128, 'received_row': 127, 'diff_row': 129, 'summary_row': 133, 'expense_col': 15}
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
            {'month': 'Apr', 'start': 121, 'end': 133}   # Apr vendor rows
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
            'Apr': 127   # Total row for Apr (Total Amount Received per Wing)
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
            {'month': 'Apr', 'vendor_row': 120}
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
    year = "2026" if month in ["Jan", "Feb", "Mar", "Apr"] else "2025"
    
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

def main():
    st.markdown('<h1 class="main-header">🏢 Zen Estate Financial Dashboard (Sep 2025 – Apr 2026)</h1>', unsafe_allow_html=True)
    
    # Auto-load data from GitHub (no upload needed)
    with st.spinner('Loading latest data from repository...'):
        df_monthly, df_wings, df_vendors, df_extra_income_breakdown, df_fines = load_excel_from_github()
    
    if not df_monthly.empty:
            # Monthly Overview Table
            st.markdown("""
                <div style='background: linear-gradient(90deg, #1f77b4 0%, #2ca02c 100%); 
                            color: white; padding: 15px; border-radius: 10px; 
                            font-size: 1.8rem; font-weight: bold; margin-bottom: 1rem;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                    📊 Monthly Overview (To Be vs Received)
                </div>
            """, unsafe_allow_html=True)
            
            overview_data = df_monthly.copy()
            overview_data['Difference'] = overview_data['To_Be'] - overview_data['Received']
            
            st.dataframe(
                overview_data[['Month', 'To_Be', 'Received', 'Difference', 'Expense']].style.format({
                    'To_Be': '₹{:,.2f}',
                    'Received': '₹{:,.2f}',
                    'Difference': '₹{:,.2f}',
                    'Expense': '₹{:,.2f}'
                }).set_properties(**{
                    'text-align': 'center'
                }).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#1f77b4'), ('color', 'white'), ('font-weight', 'bold')]}
                ]),
                use_container_width=True
            )
            
            st.markdown("---")
            
            # Vendor Breakdown - 5 separate charts for each month
            # Extra Income
            st.markdown("""
                <div style='background: linear-gradient(90deg, #9467bd 0%, #8c564b 100%); 
                            color: white; padding: 15px; border-radius: 10px; 
                            font-size: 1.8rem; font-weight: bold; margin-top: 2rem; margin-bottom: 1rem;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                    💰 Extra Income (Month-wise)
                </div>
            """, unsafe_allow_html=True)
            fig2 = create_extra_income_chart(df_monthly)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True)
            
            # Extra Income Breakdown by Source
            if not df_extra_income_breakdown.empty:
                st.markdown("""
                    <div style='background: linear-gradient(90deg, #e377c2 0%, #7f7f7f 100%); 
                                color: white; padding: 12px; border-radius: 8px; 
                                font-size: 1.4rem; font-weight: bold; margin-top: 1.5rem; margin-bottom: 1rem;
                                box-shadow: 0 3px 5px rgba(0,0,0,0.1);'>
                        📋 Extra Income Breakdown
                    </div>
                """, unsafe_allow_html=True)
                
                # Create a formatted dataframe
                breakdown_display = df_extra_income_breakdown.copy()
                
                # Add total column (all 6 income sources)
                breakdown_display['Total'] = breakdown_display[['NBH', 'Lift', 'Event', 'Scrap', 'Parking_Fine', 'ClubHouse_Booking & Gym']].sum(axis=1)
                
                # Display as table
                st.dataframe(
                    breakdown_display.style.format({
                        'NBH': '₹{:,.2f}',
                        'Lift': '₹{:,.2f}',
                        'Event': '₹{:,.2f}',
                        'Scrap': '₹{:,.2f}',
                        'Parking_Fine': '₹{:,.2f}',
                        'ClubHouse_Booking & Gym': '₹{:,.2f}',
                        'Total': '₹{:,.2f}'
                    }).set_properties(**{
                        'text-align': 'center'
                    }).set_table_styles([
                        {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#1f77b4'), ('color', 'white'), ('font-weight', 'bold')]}
                    ]),
                    use_container_width=True
                )
            
            # Wing/Shop Filter Section
            st.markdown("""
                <div style='background: linear-gradient(90deg, #ff7f0e 0%, #d62728 100%); 
                            color: white; padding: 15px; border-radius: 10px; 
                            font-size: 1.8rem; font-weight: bold; margin-top: 2rem; margin-bottom: 1rem;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                    🏢 Wing/Shop-Wise Analysis
                </div>
            """, unsafe_allow_html=True)
            
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
                        month_order = {'Sep': 1, 'Oct': 2, 'Nov': 3, 'Dec': 4, 'Jan': 5, 'Feb': 6, 'Mar': 7, 'Apr': 8}
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
                        
                        # Style the dataframe
                        def color_wing_shop_difference(val):
                            if val < 0:
                                return 'background-color: #ccffcc; font-weight: bold'  # Green for excess
                            elif val > 0:
                                return 'background-color: #ffcccc; font-weight: bold'  # Red for pending
                            else:
                                return 'background-color: #ffffcc'  # Yellow for zero
                        
                        def highlight_wing_shop_months(row):
                            colors = {
                                'Sep': 'background-color: #cce5ff',
                                'Oct': 'background-color: #ffe5cc',
                                'Nov': 'background-color: #d9ccff',
                                'Dec': 'background-color: #fff0b3',
                                'Jan': 'background-color: #ffccdd',
                                'Feb': 'background-color: #b3f0e0',
                                'Mar': 'background-color: #fff3b3',
                                'Apr': 'background-color: #ccf0cc',
                            }
                            bg = colors.get(row['Month'], '')
                            return [bg] * len(row)
                        
                        styled_wing_shop_df = wing_shop_display[['Month', 'To Be Received', 'Actual Received', 'Fine_Details', 'Pending/Excess (-ve = Excess)']].style.format({
                            'To Be Received': '₹{:,.2f}',
                            'Actual Received': '₹{:,.2f}',
                            'Pending/Excess (-ve = Excess)': '₹{:,.2f}'
                        }).apply(highlight_wing_shop_months, axis=1).map(color_wing_shop_difference, subset=['Pending/Excess (-ve = Excess)'])
                        
                        styled_wing_shop_df = styled_wing_shop_df.set_properties(**{
                            'text-align': 'center'
                        }).set_table_styles([
                            {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#1f77b4'), ('color', 'white'), ('font-weight', 'bold'), ('font-size', '1.1rem'), ('padding', '12px')]},
                            {'selector': 'td', 'props': [('padding', '10px'), ('font-size', '1rem')]}
                        ])
                        
                        st.dataframe(
                            styled_wing_shop_df,
                            use_container_width=True
                        )
                    else:
                        st.warning(f"No data available for {selected_wing_shop}")
            
            # Detailed Wing/Shop Monthly Breakdown Table
            st.markdown("""
                <div style='background: linear-gradient(90deg, #2ca02c 0%, #1f77b4 100%); 
                            color: white; padding: 15px; border-radius: 10px; 
                            font-size: 1.8rem; font-weight: bold; margin-top: 2rem; margin-bottom: 1rem;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                    📋 Wing/Shop Monthly Details
                </div>
            """, unsafe_allow_html=True)
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
                month_order = {'Sep': 1, 'Oct': 2, 'Nov': 3, 'Dec': 4, 'Jan': 5, 'Feb': 6, 'Mar': 7, 'Apr': 8}
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
                
                # Create a function to apply month backgrounds
                def highlight_months(row):
                    month = row['Month']
                    colors = {
                        'Sep': 'background-color: #cce5ff',   # Blue
                        'Oct': 'background-color: #ffe5cc',   # Orange
                        'Nov': 'background-color: #d9ccff',   # Purple
                        'Dec': 'background-color: #fff0b3',   # Amber
                        'Jan': 'background-color: #ffccdd',   # Pink
                        'Feb': 'background-color: #b3f0e0',   # Teal
                        'Mar': 'background-color: #fff3b3',   # Yellow
                        'Apr': 'background-color: #ccf0cc',   # Green
                    }
                    bg = colors.get(month, '')
                    return [bg] * len(row)
                
                # Apply styling
                styled_df = detailed_breakdown[['Wing', 'Month', 'To Be Received', 'Actual Received', 'Fine_Details', 'Difference']].style.format({
                    'To Be Received': '₹{:,.2f}',
                    'Actual Received': '₹{:,.2f}',
                    'Difference': '₹{:,.2f}'
                }).apply(highlight_months, axis=1)
                
                # Apply difference color coding on top of month backgrounds
                def color_difference(val):
                    if val < 0:
                        return 'background-color: #ccffcc; font-weight: bold'  # Green for excess
                    elif val > 0:
                        return 'background-color: #ffcccc; font-weight: bold'  # Red for pending
                    else:
                        return ''
                
                styled_df = styled_df.map(color_difference, subset=['Difference'])
                
                # Add center alignment and header styling
                styled_df = styled_df.set_properties(**{
                    'text-align': 'center'
                }).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#1f77b4'), ('color', 'white'), ('font-weight', 'bold'), ('font-size', '1.1rem'), ('padding', '12px')]},
                    {'selector': 'td', 'props': [('padding', '10px'), ('font-size', '1rem')]}
                ])
                
                # Display the table
                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    height=600
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
    else:
        st.warning("⚠️ No data found")
    
    # Error handling if data couldn't be loaded
    if df_monthly.empty:
        st.error("❌ Unable to load data from repository")
        st.info("Please ensure the Excel file is committed to the GitHub repository.")

if __name__ == "__main__":
    main()
