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

@st.cache_data
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

@st.cache_data
def load_excel_data(file):
    """Load all financial data from Excel"""
    try:
        df = pd.read_excel(file, sheet_name='Sheet1', header=None)
        
        # Wing names and their column indices
        # Mapping: wing_name -> col_idx
        wing_col_map = {
            'A Wing': 6, 'A Shop': 7, 'B Wing': 8, 'B Shop': 9, 'C Wing': 10, 'C Shop Total': 11,
            'D Wing': 14, 'D Shop': 15, 'E Wing': 16, 'E Shop': 17, 
            'F Wing': 18, 'G Wing': 19, 'H Wing': 20, 'I Wing': 21
        }
        wings = list(wing_col_map.keys())
        
        # Extract monthly data
        months_info = [
            {'name': 'Sep', 'to_be_row': 9, 'received_row': 8, 'diff_row': 10, 'summary_row': 14, 'expense_col': 15},
            {'name': 'Oct', 'to_be_row': 29, 'received_row': 28, 'diff_row': 30, 'summary_row': 34, 'expense_col': 15},
            {'name': 'Nov', 'to_be_row': 45, 'received_row': 44, 'diff_row': 46, 'summary_row': 50, 'expense_col': 15},
            {'name': 'Dec', 'to_be_row': 62, 'received_row': 61, 'diff_row': 63, 'summary_row': 67, 'expense_col': 15},
            {'name': 'Jan', 'to_be_row': 77, 'received_row': 76, 'diff_row': 78, 'summary_row': 82, 'expense_col': 15},
            {'name': 'Feb', 'to_be_col': 6, 'received_col': 9, 'diff_col': 12, 'summary_row': 100, 'expense_col': 15},
            {'name': 'Mar', 'to_be_col': 6, 'received_col': 9, 'diff_col': 12, 'summary_row': 116, 'expense_col': 15}
        ]
        
        # Monthly summary data
        monthly_data = []
        wing_data = []
        
        for month_info in months_info:
            month = month_info['name']
            summary_row = month_info['summary_row']
            
            # Get summary totals - works for all months
            to_be = df.iloc[summary_row, 6] if pd.notna(df.iloc[summary_row, 6]) else 0
            received = df.iloc[summary_row, 9] if pd.notna(df.iloc[summary_row, 9]) else 0
            expense = df.iloc[summary_row, month_info['expense_col']] if pd.notna(df.iloc[summary_row, month_info['expense_col']]) else 0
            extra_income = df.iloc[summary_row, 18] if pd.notna(df.iloc[summary_row, 18]) else 0
            
            # Extract extra income from column 18 (the actual total)
            # No breakdown data exists in the sheet yet - all 6 fields are 0
            extra_income_details = {
                'NBH': 0.0,
                'Lift': 0.0,
                'Event': 0.0,
                'Scrap': 0.0,
                'Parking_Fine': 0.0,
                'Clubhouse_Booking': 0.0
            }
            
            monthly_data.append({
                'Month': month,
                'To_Be': float(to_be),
                'Received': float(received),
                'Expense': float(expense),
                'Extra_Income': float(extra_income),
                **extra_income_details  # Spread the breakdown details
            })
            
            # Get wing-wise data
            for wing in wings:
                col_idx = wing_col_map[wing]  # Use mapping instead of enumeration
                if col_idx < df.shape[1]:
                    # Sep-Jan use row indices, Feb-Mar use summary row values
                    if 'to_be_row' in month_info:
                        to_be_val = df.iloc[month_info['to_be_row'], col_idx]
                        received_val = df.iloc[month_info['received_row'], col_idx]
                        diff_val = df.iloc[month_info['diff_row'], col_idx]
                    else:
                        # Feb-Mar: Use summary row values (same for all wings since no per-wing breakdown)
                        to_be_val = df.iloc[summary_row, month_info['to_be_col']]
                        received_val = df.iloc[summary_row, month_info['received_col']]
                        diff_val = df.iloc[summary_row, month_info['diff_col']]
                    
                    
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
            {'month': 'Feb', 'start': 88, 'end': 101},   # Feb vendor rows ✨ NEW
            {'month': 'Mar', 'start': 104, 'end': 118}   # Mar vendor rows ✨ NEW
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
        # Breakdown rows are: Summary Row + 1
        # Columns: NBH=23, Lift=24, Event=25, Scrap=26, Parking_Fine=27, Clubhouse_Booking=28
        extra_income_breakdown = []
        
        breakdown_month_rows = {
            'Sep': 15,   # Row 15 in Excel = index 14 + 1
            'Oct': 35,   # Row 35 in Excel = index 34 + 1
            'Nov': 51,   # Row 51 in Excel = index 50 + 1
            'Dec': 68,   # Row 68 in Excel = index 67 + 1
            'Jan': 83,   # Row 83 in Excel = index 82 + 1
            'Feb': 101,  # Row 101 in Excel = index 100 + 1
            'Mar': 117   # Row 117 in Excel = index 116 + 1
        }
        
        for month, row_idx in breakdown_month_rows.items():
            if row_idx < len(df):
                nbh = df.iloc[row_idx, 23] if pd.notna(df.iloc[row_idx, 23]) else 0
                lift = df.iloc[row_idx, 24] if pd.notna(df.iloc[row_idx, 24]) else 0
                event = df.iloc[row_idx, 25] if pd.notna(df.iloc[row_idx, 25]) else 0
                scrap = df.iloc[row_idx, 26] if pd.notna(df.iloc[row_idx, 26]) else 0
                parking_fine = df.iloc[row_idx, 27] if pd.notna(df.iloc[row_idx, 27]) else 0
                clubhouse_booking = df.iloc[row_idx, 28] if pd.notna(df.iloc[row_idx, 28]) else 0
                
                extra_income_breakdown.append({
                    'Month': month,
                    'NBH': float(nbh) if isinstance(nbh, (int, float)) else 0,
                    'Lift': float(lift) if isinstance(lift, (int, float)) else 0,
                    'Event': float(event) if isinstance(event, (int, float)) else 0,
                    'Scrap': float(scrap) if isinstance(scrap, (int, float)) else 0,
                    'Parking_Fine': float(parking_fine) if isinstance(parking_fine, (int, float)) else 0,
                    'Clubhouse_Booking': float(clubhouse_booking) if isinstance(clubhouse_booking, (int, float)) else 0
                })
        
        df_extra_income_breakdown = pd.DataFrame(extra_income_breakdown)
        
        # Extract Fine data from NEW STRUCTURED format
        # Structure: Row X = "Fine" header, Row X+1 = Vendors header with wing names
        # Rows X+2-X+5 = HK, Quinteze, Security, STP with values for each wing
        # Row X+6 = Total row
        # Columns: Col 30-38 contain the data
        fine_data = []
        
        fine_sections = [
            {'month': 'Sep', 'header_row': 1},      # Rows 1-7
            {'month': 'Oct', 'header_row': 20},     # Rows 20-26
            {'month': 'Nov', 'header_row': 36},     # Rows 36-42
            {'month': 'Dec', 'header_row': 53},     # Rows 53-59
            {'month': 'Jan', 'header_row': 68},     # Rows 68-74
            {'month': 'Feb', 'header_row': 86},     # Rows 86-92 (Feb Vendor Bills)
            {'month': 'Mar', 'header_row': 102}     # Rows 102-108 (Mar Vendor Bills)
        ]
        
        for section in fine_sections:
            header_row = section['header_row']
            month = section['month']
            
            # Get wing names from header row (row after "Fine")
            wing_header_row = header_row + 1
            if wing_header_row < len(df):
                # Columns 31-44 contain wing and shop names (9 wings + 5 shops)
                wings_shops = []
                for col in range(31, 45):  # Extended range to include shops (A-E Shop)
                    wing_name = df.iloc[wing_header_row, col]
                    if pd.notna(wing_name) and isinstance(wing_name, str) and ('Wing' in str(wing_name) or 'Shop' in str(wing_name)):
                        wings_shops.append((col, wing_name))
                
                # Extract fine data for each vendor type (HK, Quinteze, Security, STP)
                vendor_rows = {
                    'HK': header_row + 2,
                    'Quinteze': header_row + 3,
                    'Security': header_row + 4,
                    'STP': header_row + 5
                }
                
                # For each wing/shop, collect all fine values
                for col_idx, wing_name in wings_shops:
                    hk_fine = df.iloc[vendor_rows['HK'], col_idx] if vendor_rows['HK'] < len(df) else 0
                    quinteze_fine = df.iloc[vendor_rows['Quinteze'], col_idx] if vendor_rows['Quinteze'] < len(df) else 0
                    security_fine = df.iloc[vendor_rows['Security'], col_idx] if vendor_rows['Security'] < len(df) else 0
                    stp_fine = df.iloc[vendor_rows['STP'], col_idx] if vendor_rows['STP'] < len(df) else 0
                    
                    hk_fine = float(hk_fine) if pd.notna(hk_fine) and isinstance(hk_fine, (int, float)) else 0
                    quinteze_fine = float(quinteze_fine) if pd.notna(quinteze_fine) and isinstance(quinteze_fine, (int, float)) else 0
                    security_fine = float(security_fine) if pd.notna(security_fine) and isinstance(security_fine, (int, float)) else 0
                    stp_fine = float(stp_fine) if pd.notna(stp_fine) and isinstance(stp_fine, (int, float)) else 0
                    
                    total_fine = hk_fine + quinteze_fine + security_fine + stp_fine
                    
                    fine_data.append({
                        'Month': month,
                        'Wing': wing_name,
                        'HK': hk_fine,
                        'Quinteze': quinteze_fine,
                        'Security': security_fine,
                        'STP': stp_fine,
                        'Total_Fine': total_fine
                    })
        
        df_fines = pd.DataFrame(fine_data) if fine_data else pd.DataFrame()
        
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
    year = "2026" if month == "Jan" else "2025"
    
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
    st.markdown('<h1 class="main-header">🏢 Zen Estate Financial Dashboard (Sep 2025 – Mar 2026)</h1>', unsafe_allow_html=True)
    
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
            if not df_vendors.empty:
                st.markdown("""
                    <div style='background: linear-gradient(90deg, #ff7f0e 0%, #d62728 100%); 
                                color: white; padding: 15px; border-radius: 10px; 
                                font-size: 1.8rem; font-weight: bold; margin-top: 2rem; margin-bottom: 1rem;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                        💼 Vendor Expense Breakdown (Month-wise)
                    </div>
                """, unsafe_allow_html=True)
                
                # September
                fig_sep = create_vendor_breakdown(df_vendors, 'Sep')
                if fig_sep:
                    st.plotly_chart(fig_sep, use_container_width=True)
                
                # October
                fig_oct = create_vendor_breakdown(df_vendors, 'Oct')
                if fig_oct:
                    st.plotly_chart(fig_oct, use_container_width=True)
                
                # November
                fig_nov = create_vendor_breakdown(df_vendors, 'Nov')
                if fig_nov:
                    st.plotly_chart(fig_nov, use_container_width=True)
                
                # December
                fig_dec = create_vendor_breakdown(df_vendors, 'Dec')
                if fig_dec:
                    st.plotly_chart(fig_dec, use_container_width=True)
                
                # January
                fig_jan = create_vendor_breakdown(df_vendors, 'Jan')
                if fig_jan:
                    st.plotly_chart(fig_jan, use_container_width=True)
                
                # February ✨ NEW
                fig_feb = create_vendor_breakdown(df_vendors, 'Feb')
                if fig_feb:
                    st.plotly_chart(fig_feb, use_container_width=True)
                
                # March ✨ NEW
                fig_mar = create_vendor_breakdown(df_vendors, 'Mar')
                if fig_mar:
                    st.plotly_chart(fig_mar, use_container_width=True)
            
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
                
                # Check which columns exist and add total only if breakdown columns exist
                breakdown_cols = []
                for col in ['NBH', 'Lift', 'Event', 'Scrap', 'Parking_Fine', 'Clubhouse_Booking']:
                    if col in breakdown_display.columns:
                        breakdown_cols.append(col)
                
                # Add total column only if we have breakdown columns
                if breakdown_cols:
                    breakdown_display['Total'] = breakdown_display[breakdown_cols].sum(axis=1)
                    
                    # Display columns: Month + breakdown columns + Total
                    display_cols = ['Month'] + breakdown_cols + ['Total']
                    # Filter to only columns that exist
                    display_cols = [col for col in display_cols if col in breakdown_display.columns]
                    
                    # Format dictionary
                    format_dict = {col: '₹{:,.2f}' for col in display_cols if col != 'Month'}
                    
                    st.dataframe(
                        breakdown_display[display_cols].style.format(format_dict).set_properties(**{
                            'text-align': 'center'
                        }).set_table_styles([
                            {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#1f77b4'), ('color', 'white'), ('font-weight', 'bold')]}
                        ]),
                    use_container_width=True
                )
            
            # Wing/Shop Analysis
            st.markdown("""
                <div style='background: linear-gradient(90deg, #17becf 0%, #bcbd22 100%); 
                            color: white; padding: 15px; border-radius: 10px; 
                            font-size: 1.8rem; font-weight: bold; margin-top: 2rem; margin-bottom: 1rem;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                    🏘️ Pending/Excess Amount Received by Wing/Shop
                </div>
            """, unsafe_allow_html=True)
            if not df_wings.empty:
                # Filter out C Shop Rahul and C Shop Sagar before creating chart
                df_wings_filtered = df_wings[~df_wings['Wing'].isin(['C Shop Rahul', 'C Shop Sagar'])]
                fig4 = create_wing_difference_chart(df_wings_filtered)
                if fig4:
                    st.plotly_chart(fig4, use_container_width=True)
            
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
                
                # Remove C Shop Rahul and C Shop Sagar (they have no data)
                all_wings_shops = [w for w in all_wings_shops if w not in ['C Shop Rahul', 'C Shop Sagar']]
                
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
                        # Extract fine data for both wings AND shops ✨
                        wing_shop_fines = df_fines[df_fines['Wing'] == selected_wing_shop].copy() if not df_fines.empty else pd.DataFrame()
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
                        # Sort by month chronologically (Sep, Oct, Nov, Dec, Jan)
                        month_order = {'Sep': 1, 'Oct': 2, 'Nov': 3, 'Dec': 4, 'Jan': 5, 'Feb': 6, 'Mar': 7}
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
                        
                        styled_wing_shop_df = wing_shop_display[['Month', 'To Be Received', 'Actual Received', 'Fine_Details', 'Pending/Excess (-ve = Excess)']].style.format({
                            'To Be Received': '₹{:,.2f}',
                            'Actual Received': '₹{:,.2f}',
                            'Pending/Excess (-ve = Excess)': '₹{:,.2f}'
                        }).apply(
                            lambda x: [
                                'background-color: #ccffcc; font-weight: bold' if isinstance(val, (int, float)) and val < 0
                                else 'background-color: #ffcccc; font-weight: bold' if isinstance(val, (int, float)) and val > 0 
                                else 'background-color: #ffffcc' if isinstance(val, (int, float)) and val == 0
                                else ''
                                for val in x
                            ] if x.name == 'Pending/Excess (-ve = Excess)' else [''] * len(x),
                            axis=0
                        )
                        
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
                        
                        # Display detailed FINE BREAKDOWN if this wing has fines
                        if not wing_shop_fines.empty:
                            st.subheader(f"💰 {selected_wing_shop} - Fine Details Breakdown")
                            
                            # Create a detailed fine breakdown table
                            fine_display = wing_shop_fines.copy()
                            fine_display = fine_display[['Month', 'HK', 'Quinteze', 'Security', 'STP', 'Total_Fine']]
                            
                            # Format and style the fine table
                            styled_fine_df = fine_display.style.format({
                                'HK': '₹{:,.2f}',
                                'Quinteze': '₹{:,.2f}',
                                'Security': '₹{:,.2f}',
                                'STP': '₹{:,.2f}',
                                'Total_Fine': '₹{:,.2f}'
                            }).apply(
                                lambda x: [
                                    'background-color: #ffe6e6; font-weight: bold' if val > 0 
                                    else ''
                                    for val in x
                                ] if x.name in ['HK', 'Quinteze', 'Security', 'STP', 'Total_Fine'] else [''] * len(x),
                                axis=0
                            )
                            
                            styled_fine_df = styled_fine_df.set_properties(**{
                                'text-align': 'center'
                            }).set_table_styles([
                                {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#d32f2f'), ('color', 'white'), ('font-weight', 'bold'), ('font-size', '1rem'), ('padding', '12px')]},
                                {'selector': 'td', 'props': [('padding', '10px'), ('font-size', '0.95rem')]}
                            ])
                            
                            st.dataframe(
                                styled_fine_df,
                                use_container_width=True
                            )
                            
                            # Show summary statistics
                            fine_summary_cols = st.columns(4)
                            with fine_summary_cols[0]:
                                hk_total = wing_shop_fines['HK'].sum()
                                st.metric("HK Fines", f"₹{hk_total:,.2f}")
                            with fine_summary_cols[1]:
                                quinteze_total = wing_shop_fines['Quinteze'].sum()
                                st.metric("Quinteze Fines", f"₹{quinteze_total:,.2f}")
                            with fine_summary_cols[2]:
                                security_total = wing_shop_fines['Security'].sum()
                                st.metric("Security Fines", f"₹{security_total:,.2f}")
                            with fine_summary_cols[3]:
                                stp_total = wing_shop_fines['STP'].sum()
                                st.metric("STP Fines", f"₹{stp_total:,.2f}")
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
                st.markdown("**Monthly breakdown showing To Be Received, Actual Received, and Difference for each Wing/Shop** *(Sorted by Wing/Shop name)*")
                
                # Format the dataframe for better display
                detailed_breakdown = df_wings.copy()
                
                # Remove C Shop Rahul and C Shop Sagar (they have no data)
                detailed_breakdown = detailed_breakdown[~detailed_breakdown['Wing'].isin(['C Shop Rahul', 'C Shop Sagar'])]
                
                # Create a custom sort order for months
                month_order = {'Sep': 1, 'Oct': 2, 'Nov': 3, 'Dec': 4, 'Jan': 5, 'Feb': 6, 'Mar': 7}
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
                
                # Create a function to apply alternating month backgrounds
                def highlight_months(row):
                    month = row['Month']
                    # Assign background colors based on month
                    if month == 'Sep':
                        return ['background-color: #e6f2ff'] * len(row)  # Light blue
                    elif month == 'Oct':
                        return ['background-color: #fff4e6'] * len(row)  # Light orange
                    elif month == 'Nov':
                        return ['background-color: #e6ffe6'] * len(row)  # Light green
                    elif month == 'Dec':
                        return ['background-color: #ffe6f2'] * len(row)  # Light pink
                    elif month == 'Jan':
                        return ['background-color: #f2e6ff'] * len(row)  # Light purple
                    else:
                        return [''] * len(row)
                
                # Apply styling
                styled_df = detailed_breakdown[['Wing', 'Month', 'To Be Received', 'Actual Received', 'Difference']].style.format({
                    'To Be Received': '₹{:,.2f}',
                    'Actual Received': '₹{:,.2f}',
                    'Difference': '₹{:,.2f}'
                }).apply(highlight_months, axis=1)
                
                # Apply difference color coding on top of month backgrounds
                def color_difference(x):
                    if x.name == 'Difference':
                        return [
                            'background-color: #ccffcc; font-weight: bold' if val < 0
                            else 'background-color: #ffcccc; font-weight: bold' if val > 0
                            else ''
                            for val in x
                        ]
                    return [''] * len(x)
                
                styled_df = styled_df.apply(color_difference, axis=0)
                
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
