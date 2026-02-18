import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Zen Estate Financial Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_excel_data(file):
    """Load and process data from uploaded Excel file"""
    
    # Load summary data from Sheet3
    df_sheet3 = pd.read_excel(file, sheet_name='Sheet3', header=None)
    
    # Extract monthly summary data
    monthly_data = []
    
    # September data (rows 20-23)
    sep_data = {
        'Month': 'Sep',
        'To_Be': float(df_sheet3.iloc[21, 1]) if pd.notna(df_sheet3.iloc[21, 1]) else 0,
        'Received': float(df_sheet3.iloc[22, 1]) if pd.notna(df_sheet3.iloc[22, 1]) else 0,
        'Difference': float(df_sheet3.iloc[23, 1]) if pd.notna(df_sheet3.iloc[23, 1]) else 0
    }
    monthly_data.append(sep_data)
    
    # October data (rows 25-28)
    oct_data = {
        'Month': 'Oct',
        'To_Be': float(df_sheet3.iloc[26, 1]) if pd.notna(df_sheet3.iloc[26, 1]) else 0,
        'Received': float(df_sheet3.iloc[27, 1]) if pd.notna(df_sheet3.iloc[27, 1]) else 0,
        'Difference': float(df_sheet3.iloc[28, 1]) if pd.notna(df_sheet3.iloc[28, 1]) else 0
    }
    monthly_data.append(oct_data)
    
    # November data (rows 30-33)
    nov_data = {
        'Month': 'Nov',
        'To_Be': float(df_sheet3.iloc[31, 1]) if pd.notna(df_sheet3.iloc[31, 1]) else 0,
        'Received': float(df_sheet3.iloc[32, 1]) if pd.notna(df_sheet3.iloc[32, 1]) else 0,
        'Difference': float(df_sheet3.iloc[33, 1]) if pd.notna(df_sheet3.iloc[33, 1]) else 0
    }
    monthly_data.append(nov_data)
    
    df_monthly = pd.DataFrame(monthly_data)
    
    # Extract Wing/Shop data for all three months
    wings = ['A Wing', 'A Shop', 'B Wing', 'B Shop', 'C Wing', 'C Shop', 
             'D Wing', 'D Shop', 'E Wing', 'E Shop', 'F Wing', 'G Wing', 'H Wing', 'I Wing']
    
    wing_data = []
    for idx, wing in enumerate(wings):
        col_idx = idx + 1
        
        # Get data from all three months
        sep_to_be = float(df_sheet3.iloc[21, col_idx]) if pd.notna(df_sheet3.iloc[21, col_idx]) else 0
        sep_received = float(df_sheet3.iloc[22, col_idx]) if pd.notna(df_sheet3.iloc[22, col_idx]) else 0
        
        oct_to_be = float(df_sheet3.iloc[26, col_idx]) if pd.notna(df_sheet3.iloc[26, col_idx]) else 0
        oct_received = float(df_sheet3.iloc[27, col_idx]) if pd.notna(df_sheet3.iloc[27, col_idx]) else 0
        
        nov_to_be = float(df_sheet3.iloc[31, col_idx]) if pd.notna(df_sheet3.iloc[31, col_idx]) else 0
        nov_received = float(df_sheet3.iloc[32, col_idx]) if pd.notna(df_sheet3.iloc[32, col_idx]) else 0
        
        total_to_be = sep_to_be + oct_to_be + nov_to_be
        total_received = sep_received + oct_received + nov_received
        difference = total_received - total_to_be
        
        wing_data.append({
            'Wing': wing,
            'To_Be': total_to_be,
            'Received': total_received,
            'Difference': difference
        })
    
    df_wings = pd.DataFrame(wing_data)
    
    # Load expense data from first sheet
    df_sheet1 = pd.read_excel(file, sheet_name='Sheet1', header=None)
    
    # Parse vendor expenses - this is a simplified version
    # You may need to adjust based on exact structure
    vendor_data = []
    
    return df_monthly, df_wings, vendor_data

def create_monthly_overview_chart(df):
    """Create monthly overview bar chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='To Be Received',
        x=df['Month'],
        y=df['To_Be'],
        marker_color='#1f77b4',
        text=[f'₹{val:,.0f}' for val in df['To_Be']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>To Be: ₹%{y:,.0f}<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        name='Received',
        x=df['Month'],
        y=df['Received'],
        marker_color='#2ca02c',
        text=[f'₹{val:,.0f}' for val in df['Received']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Received: ₹%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Monthly Overview: To Be vs Received',
        xaxis_title='Month',
        yaxis_title='Amount (INR)',
        barmode='group',
        height=500,
        hovermode='x unified',
        plot_bgcolor='#E5ECF6',
        yaxis=dict(tickprefix='₹', tickformat=',.0f')
    )
    
    return fig

def create_line_chart(df):
    """Create line chart for trends"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['To_Be'],
        mode='lines+markers',
        name='To Be Received',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=10)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['Received'],
        mode='lines+markers',
        name='Received',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title='Monthly Trend: Amount To Be Received vs Received',
        xaxis_title='Month',
        yaxis_title='Amount (INR)',
        height=400,
        hovermode='x unified',
        plot_bgcolor='#E5ECF6',
        yaxis=dict(tickprefix='₹', tickformat=',.0f')
    )
    
    return fig

def create_wing_difference_chart(df):
    """Create wing/shop difference chart"""
    # Sort by difference
    df_sorted = df.sort_values('Difference', ascending=True)
    
    # Color code: green for positive (excess), red for negative (pending), gray for zero
    colors = ['#2ca02c' if val > 0 else '#d62728' if val < 0 else '#9e9e9e' 
              for val in df_sorted['Difference']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_sorted['Wing'],
        y=df_sorted['Difference'],
        marker_color=colors,
        text=[f'₹{val:,.2f}' for val in df_sorted['Difference']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Difference: ₹%{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Pending (Red) / Excess (Green) by Wing/Shop',
        xaxis_title='Wing / Shop',
        yaxis_title='Amount (INR)',
        height=500,
        plot_bgcolor='#E5ECF6',
        yaxis=dict(tickprefix='₹', tickformat=',.2f')
    )
    
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">🏢 Zen Estate Financial Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 Upload Data")
        uploaded_file = st.file_uploader(
            "Upload Excel File", 
            type=['xlsx', 'xls'],
            help="Upload your Zen Estate expense Excel file"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Dashboard Features")
        st.markdown("""
        - 📈 Monthly Revenue Overview
        - 💰 Wing/Shop Analysis
        - 📉 Trends & Comparisons
        - 🔄 Auto-refresh Data
        """)
        
        st.markdown("---")
        st.info("💡 Upload your Excel file to see live data")
    
    # Main content
    if uploaded_file is not None:
        try:
            # Load data
            with st.spinner('Loading data...'):
                df_monthly, df_wings, vendor_data = load_excel_data(uploaded_file)
            
            st.success('✅ Data loaded successfully!')
            
            # Key Metrics Row
            st.markdown("### 📊 Key Metrics")
            col1, col2, col3, col4 = st.columns(4)
            
            total_to_be = df_monthly['To_Be'].sum()
            total_received = df_monthly['Received'].sum()
            total_difference = total_received - total_to_be
            collection_rate = (total_received / total_to_be * 100) if total_to_be > 0 else 0
            
            with col1:
                st.metric(
                    label="Total To Be Received",
                    value=f"₹{total_to_be:,.0f}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="Total Received",
                    value=f"₹{total_received:,.0f}",
                    delta=f"₹{total_difference:,.0f}" if total_difference != 0 else "On Track"
                )
            
            with col3:
                st.metric(
                    label="Collection Rate",
                    value=f"{collection_rate:.1f}%",
                    delta=f"{collection_rate - 100:.1f}%" if collection_rate < 100 else "Perfect"
                )
            
            with col4:
                pending_count = len(df_wings[df_wings['Difference'] < 0])
                st.metric(
                    label="Wings with Pending",
                    value=f"{pending_count}",
                    delta=f"{14 - pending_count} clear" if pending_count > 0 else "All Clear!"
                )
            
            st.markdown("---")
            
            # Monthly Overview
            st.markdown("### 📈 Monthly Revenue Analysis")
            tab1, tab2, tab3 = st.tabs(["📊 Bar Chart", "📉 Line Trend", "📋 Data Table"])
            
            with tab1:
                fig_monthly = create_monthly_overview_chart(df_monthly)
                st.plotly_chart(fig_monthly, use_container_width=True)
            
            with tab2:
                fig_line = create_line_chart(df_monthly)
                st.plotly_chart(fig_line, use_container_width=True)
            
            with tab3:
                st.dataframe(
                    df_monthly.style.format({
                        'To_Be': '₹{:,.2f}',
                        'Received': '₹{:,.2f}',
                        'Difference': '₹{:,.2f}'
                    }),
                    use_container_width=True
                )
            
            st.markdown("---")
            
            # Wing/Shop Analysis
            st.markdown("### 🏘️ Wing/Shop Analysis")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig_wings = create_wing_difference_chart(df_wings)
                st.plotly_chart(fig_wings, use_container_width=True)
            
            with col2:
                st.markdown("#### Summary")
                
                excess_wings = df_wings[df_wings['Difference'] > 0]
                pending_wings = df_wings[df_wings['Difference'] < 0]
                
                if len(excess_wings) > 0:
                    st.success(f"✅ **{len(excess_wings)} Wings with Excess Payment**")
                    for _, row in excess_wings.iterrows():
                        st.write(f"- {row['Wing']}: ₹{row['Difference']:,.2f}")
                
                if len(pending_wings) > 0:
                    st.error(f"⚠️ **{len(pending_wings)} Wings with Pending Payment**")
                    for _, row in pending_wings.nsmallest(5, 'Difference').iterrows():
                        st.write(f"- {row['Wing']}: ₹{row['Difference']:,.2f}")
            
            st.markdown("---")
            
            # Detailed Wing Data Table
            st.markdown("### 📋 Detailed Wing/Shop Data")
            
            # Add color coding to dataframe
            def color_difference(val):
                if val > 0:
                    return 'background-color: #d4edda'
                elif val < 0:
                    return 'background-color: #f8d7da'
                else:
                    return 'background-color: #f0f0f0'
            
            styled_df = df_wings.style.format({
                'To_Be': '₹{:,.2f}',
                'Received': '₹{:,.2f}',
                'Difference': '₹{:,.2f}'
            }).applymap(color_difference, subset=['Difference'])
            
            st.dataframe(styled_df, use_container_width=True)
            
            # Download section
            st.markdown("---")
            st.markdown("### 📥 Download Reports")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Download monthly summary
                csv_monthly = df_monthly.to_csv(index=False)
                st.download_button(
                    label="📊 Download Monthly Summary (CSV)",
                    data=csv_monthly,
                    file_name=f"zen_estate_monthly_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Download wing data
                csv_wings = df_wings.to_csv(index=False)
                st.download_button(
                    label="🏘️ Download Wing Data (CSV)",
                    data=csv_wings,
                    file_name=f"zen_estate_wing_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            st.info("Please make sure your Excel file has the correct format.")
    
    else:
        # Welcome screen
        st.markdown("""
        ### 👋 Welcome to Zen Estate Financial Dashboard
        
        This interactive dashboard helps you visualize and analyze your financial data.
        
        #### 🚀 Getting Started:
        1. Upload your Excel file using the sidebar
        2. View real-time analytics and visualizations
        3. Download reports as needed
        
        #### 📊 Features:
        - **Monthly Overview**: Track revenue collection vs targets
        - **Wing Analysis**: Monitor pending and excess payments by wing/shop
        - **Trend Analysis**: Visualize financial trends over time
        - **Export Data**: Download reports in CSV format
        
        #### 📁 File Requirements:
        - Excel file format (.xlsx or .xls)
        - Must contain Sheet3 with monthly billing data
        - Organized by Wing/Shop
        
        **👈 Upload your file from the sidebar to begin!**
        """)
        
        # Sample visualization
        st.markdown("---")
        st.markdown("### 📸 Preview")
        st.info("Once you upload your Excel file, you'll see interactive charts and analytics here!")

if __name__ == "__main__":
    main()
