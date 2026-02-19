import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
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
def load_vendor_data(file):
    """Load vendor expense data from Excel"""
    try:
        df = pd.read_excel(file, sheet_name='Sheet1', header=None)
        
        months_data = []
        for idx, row in df.iterrows():
            cell_value = str(row[0]) if pd.notna(row[0]) else ""
            if "Vendor Bills" in cell_value:
                for month in ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb"]:
                    if month in cell_value:
                        months_data.append({'month': month, 'start_row': idx + 2})
                        break
        
        monthly_totals = []
        all_vendors = []
        
        for i, month_info in enumerate(months_data):
            month = month_info['month']
            start_row = month_info['start_row']
            end_row = months_data[i + 1]['start_row'] - 3 if i < len(months_data) - 1 else len(df)
            
            month_data = df.iloc[start_row:end_row]
            total = 0
            
            for _, row in month_data.iterrows():
                for col in range(2, len(row)):
                    val = row[col]
                    if pd.notna(val) and isinstance(val, (int, float)) and val > 0:
                        total += val
                        vendor = str(row[2]) if pd.notna(row[2]) else "Unknown"
                        all_vendors.append({'vendor': vendor, 'amount': val, 'month': month})
            
            monthly_totals.append({'Month': month, 'Total_Expense': total})
        
        return pd.DataFrame(monthly_totals), pd.DataFrame(all_vendors)
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame(), pd.DataFrame()

def main():
    st.markdown('<h1 class="main-header">🏢 Zen Estate Financial Dashboard</h1>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("📁 Upload Data")
        uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])
        st.markdown("---")
        st.info("💡 Upload your Excel file to see live data")
    
    if uploaded_file:
        df_monthly, df_vendors = load_vendor_data(uploaded_file)
        
        if not df_monthly.empty:
            st.success('✅ Data loaded!')
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Expenses", f"₹{df_monthly['Total_Expense'].sum():,.0f}")
            with col2:
                st.metric("Months", len(df_monthly))
            with col3:
                st.metric("Vendors", df_vendors['vendor'].nunique() if not df_vendors.empty else 0)
            
            st.markdown("### 📈 Monthly Expenses")
            fig = go.Figure(data=[go.Bar(
                x=df_monthly['Month'],
                y=df_monthly['Total_Expense'],
                marker_color='#EF553B',
                text=[f'₹{v:,.0f}' for v in df_monthly['Total_Expense']],
                textposition='outside'
            )])
            fig.update_layout(
                xaxis_title='Month',
                yaxis_title='Amount (INR)',
                height=500,
                yaxis=dict(tickprefix='₹')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            if not df_vendors.empty:
                st.markdown("### 💼 Top Vendors")
                vendor_totals = df_vendors.groupby('vendor')['amount'].sum().sort_values(ascending=False).head(10)
                
                fig2 = go.Figure(data=[go.Bar(
                    x=vendor_totals.values,
                    y=vendor_totals.index,
                    orientation='h',
                    marker_color='#1f77b4',
                    text=[f'₹{v:,.0f}' for v in vendor_totals.values]
                )])
                fig2.update_layout(
                    xaxis_title='Amount (INR)',
                    yaxis_title='Vendor',
                    height=500
                )
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No data found")
    else:
        st.markdown("""
        ### 👋 Welcome!
        Upload your Excel file to visualize vendor expenses.
        **👈 Upload from sidebar to begin!**
        """)

if __name__ == "__main__":
    main()
