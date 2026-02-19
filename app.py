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
    </style>
""", unsafe_allow_html=True)

@st.cache_data
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
            {'name': 'Dec', 'to_be_row': 62, 'received_row': 61, 'diff_row': 63, 'summary_row': 67, 'expense_col': 15}
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
        
        # Get vendor data for December (as shown in HTML)
        vendor_data = []
        dec_start = 54
        dec_end = 67
        
        for idx in range(dec_start + 2, dec_end):
            vendor = df.iloc[idx, 2]
            amount = df.iloc[idx, 3]
            if pd.notna(vendor) and pd.notna(amount) and isinstance(amount, (int, float)) and amount > 0:
                vendor_data.append({
                    'Vendor': str(vendor),
                    'Amount': float(amount)
                })
        
        df_monthly = pd.DataFrame(monthly_data)
        df_wings = pd.DataFrame(wing_data)
        df_vendors = pd.DataFrame(vendor_data) if vendor_data else pd.DataFrame()
        
        return df_monthly, df_wings, df_vendors
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def create_vendor_breakdown(df_vendors):
    """Vendor Expense Breakdown with color gradient"""
    if df_vendors.empty:
        return None
    
    # Sort and take top vendors
    df_sorted = df_vendors.sort_values('Amount', ascending=False).head(15)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_sorted['Vendor'],
        y=df_sorted['Amount'],
        marker=dict(
            color=df_sorted['Amount'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Amount Paid")
        ),
        text=[f'₹{v:,.2f}' for v in df_sorted['Amount']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Amount: ₹%{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Vendor Expense Breakdown (Dec 2025) — Sorted High→Low',
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
        hovertemplate='<b>%{x}</b><br>Extra Income: ₹%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Extra Income by Month',
        xaxis_title='Month',
        yaxis_title='Amount (INR)',
        height=420,
        yaxis=dict(tickprefix='₹', tickformat=',.0f')
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
    
    fig.add_trace(go.Scatter(
        x=df_monthly['Month'],
        y=df_monthly['Extra_Income'],
        mode='lines+markers',
        name='Extra Income',
        line=dict(color='#FFA15A', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title='Month-wise Comparison (Using Total Monthly Expense)',
        xaxis_title='Month',
        yaxis_title='Amount (INR)',
        height=520,
        yaxis=dict(tickprefix='₹', tickformat=',.0f')
    ))
    
    return fig

def create_wing_difference_chart(df_wings):
    """Pending/Excess Amount by Wing/Shop"""
    # Aggregate total difference per wing across all months
    wing_totals = df_wings.groupby('Wing')['Difference'].sum().reset_index()
    
    # Create color array: green for positive, red for negative, gray for zero
    colors = []
    for diff in wing_totals['Difference']:
        if diff > 0:
            colors.append('#2ca02c')  # Green
        elif diff < 0:
            colors.append('#d62728')  # Red
        else:
            colors.append('#9e9e9e')  # Gray
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=wing_totals['Wing'],
        y=wing_totals['Difference'],
        marker_color=colors,
        text=[f'₹{v:,.2f}' for v in wing_totals['Difference']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Difference: ₹%{y:,.2f}<extra></extra>'
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
    st.markdown('<h1 class="main-header">🏢 Zen Estate Financial Dashboard (Sep–Dec 2025)</h1>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("📁 Upload Data")
        uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])
        st.markdown("---")
        st.markdown("### 📊 Dashboard Sections")
        st.markdown("""
        - Vendor Expense Breakdown
        - Extra Income by Month
        - Combined Monthly Comparison
        - Wing/Shop Analysis
        """)
        st.info("💡 Upload your Excel file to see live data")
    
    if uploaded_file:
        df_monthly, df_wings, df_vendors = load_excel_data(uploaded_file)
        
        if not df_monthly.empty:
            st.success('✅ Data loaded successfully!')
            
            # Monthly Overview Table
            st.markdown("### 📊 Monthly Overview (To Be vs Received, Difference = To Be − Received)")
            
            overview_data = df_monthly.copy()
            overview_data['Difference'] = overview_data['To_Be'] - overview_data['Received']
            
            st.dataframe(
                overview_data[['Month', 'To_Be', 'Received', 'Difference']].style.format({
                    'To_Be': '₹{:,.2f}',
                    'Received': '₹{:,.2f}',
                    'Difference': '₹{:,.2f}'
                }),
                use_container_width=True
            )
            
            st.markdown("---")
            
            # Vendor Breakdown
            if not df_vendors.empty:
                fig1 = create_vendor_breakdown(df_vendors)
                if fig1:
                    st.plotly_chart(fig1, use_container_width=True)
            
            # Extra Income
            st.markdown("### 💰 Extra Income (Month-wise)")
            fig2 = create_extra_income_chart(df_monthly)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True)
            
            # Combined Monthly
            st.markdown("### 📈 Combined Month-wise — To Be, Received, Expenses, Extra Income")
            fig3 = create_combined_monthly_chart(df_monthly)
            if fig3:
                st.plotly_chart(fig3, use_container_width=True)
            
            # Wing/Shop Analysis
            st.markdown("### 🏘️ Pending/Excess Amount Received by Wing/Shop")
            if not df_wings.empty:
                fig4 = create_wing_difference_chart(df_wings)
                if fig4:
                    st.plotly_chart(fig4, use_container_width=True)
            
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
    else:
        st.markdown("""
        ### 👋 Welcome to Zen Estate Financial Dashboard
        
        Upload your Excel file to visualize:
        - **Vendor Expense Breakdown** with color-coded amounts
        - **Extra Income** tracking by month
        - **Combined Monthly View** of To Be, Received, Expenses, and Extra Income
        - **Wing/Shop Analysis** showing pending (red) and excess (green) amounts
        
        **👈 Upload your file from the sidebar to begin!**
        """)

if __name__ == "__main__":
    main()
