import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
import base64

# Page configuration
st.set_page_config(
    page_title="Enhanced Excel Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 1rem;
        border: 2px dashed #dee2e6;
        text-align: center;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #1565c0;
    }
    .filter-section {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def load_and_process_data(uploaded_file):
    """Load and process the uploaded file"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Convert numeric columns to proper types
        numeric_columns = ['requestedcount', 'submittedcount', 'sentcount', 'deliveredcount', 
                          'readcount', 'failedcount', 'notsentcount']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def calculate_delivery_metrics(df):
    """Calculate delivery metrics for the data"""
    metrics = {}
    
    # Basic counts
    metrics['total_requests'] = df['requestedcount'].sum()
    metrics['total_sent'] = df['sentcount'].sum()
    metrics['total_delivered'] = df['deliveredcount'].sum()
    metrics['total_submitted'] = df['submittedcount'].sum()
    metrics['total_failed'] = df['failedcount'].sum()
    metrics['total_pending'] = df['pendingcount'].sum()
    metrics['total_not_sent'] = df['notsentcount'].sum()
    
    # Calculate percentages
    if metrics['total_requests'] > 0:
        metrics['sent_percentage'] = (metrics['total_sent'] / metrics['total_requests']) * 100
        metrics['delivered_percentage'] = (metrics['total_delivered'] / metrics['total_requests']) * 100
        metrics['submitted_percentage'] = (metrics['total_submitted'] / metrics['total_requests']) * 100
        metrics['failed_percentage'] = (metrics['total_failed'] / metrics['total_requests']) * 100
        metrics['pending_percentage'] = (metrics['total_pending'] / metrics['total_requests']) * 100
        metrics['not_sent_percentage'] = (metrics['total_not_sent'] / metrics['total_requests']) * 100
    else:
        metrics['sent_percentage'] = 0
        metrics['delivered_percentage'] = 0
        metrics['submitted_percentage'] = 0
        metrics['failed_percentage'] = 0
        metrics['pending_percentage'] = 0
        metrics['not_sent_percentage'] = 0
    
    return metrics

def analyze_pricing_model_metrics(df):
    """Analyze metrics by pricing model"""
    if 'pricingmodel' not in df.columns:
        return pd.DataFrame()
    
    pricing_analysis = df.groupby('pricingmodel').agg({
        'sentcount': 'sum',
        'deliveredcount': 'sum',
        'requestedcount': 'sum',
        'submittedcount': 'sum'
    }).reset_index()
    
    # Calculate percentages
    total_requests = df['requestedcount'].sum()
    pricing_analysis['sent_percentage'] = (pricing_analysis['sentcount'] / pricing_analysis['requestedcount']) * 100
    pricing_analysis['delivered_percentage'] = (pricing_analysis['deliveredcount'] / pricing_analysis['requestedcount']) * 100
    pricing_analysis['submitted_percentage'] = (pricing_analysis['submittedcount'] / pricing_analysis['requestedcount']) * 100
    
    return pricing_analysis

def analyze_country_metrics(df):
    """Analyze metrics by country"""
    if 'country' not in df.columns:
        return pd.DataFrame()
    
    country_analysis = df.groupby('country').agg({
        'deliveredcount': 'sum',
        'submittedcount': 'sum',
        'requestedcount': 'sum'
    }).reset_index()
    
    # Calculate percentages
    country_analysis['delivered_percentage'] = (country_analysis['deliveredcount'] / country_analysis['requestedcount']) * 100
    country_analysis['submitted_percentage'] = (country_analysis['submittedcount'] / country_analysis['requestedcount']) * 100
    
    return country_analysis.sort_values('deliveredcount', ascending=False)

def analyze_account_failures(df):
    """Analyze account IDs with highest failures"""
    if 'accountid' not in df.columns:
        return pd.DataFrame()
    
    account_failures = df.groupby('accountid').agg({
        'failedcount': 'sum',
        'requestedcount': 'sum',
        'tmplid': 'nunique'
    }).reset_index()
    
    account_failures['failure_rate'] = (account_failures['failedcount'] / account_failures['requestedcount']) * 100
    account_failures = account_failures.sort_values('failure_rate', ascending=False)
    
    return account_failures

def analyze_template_failures(df):
    """Analyze templates with maximum failures"""
    if 'tmplid' not in df.columns or 'tmplname' not in df.columns:
        return pd.DataFrame()
    
    template_failures = df.groupby(['tmplid', 'tmplname', 'accountid']).agg({
        'failedcount': 'sum',
        'requestedcount': 'sum'
    }).reset_index()
    
    template_failures['failure_rate'] = (template_failures['failedcount'] / template_failures['requestedcount']) * 100
    template_failures = template_failures.sort_values('failure_rate', ascending=False)
    
    return template_failures

def analyze_pricing_delivery_table(df):
    """Create pricing model, pricing type and delivered table"""
    if 'pricingmodel' not in df.columns:
        return pd.DataFrame()
    
    columns_to_group = ['pricingmodel']
    if 'pricingtype' in df.columns:
        columns_to_group.append('pricingtype')
    
    pricing_delivery = df.groupby(columns_to_group).agg({
        'deliveredcount': 'sum',
        'requestedcount': 'sum'
    }).reset_index()
    
    pricing_delivery['delivery_rate'] = (pricing_delivery['deliveredcount'] / pricing_delivery['requestedcount']) * 100
    
    return pricing_delivery.sort_values('delivery_rate', ascending=False)

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Enhanced Excel Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Advanced analytics for email/SMS delivery data with comprehensive metrics and insights</p>', unsafe_allow_html=True)
    
    # File upload
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Choose an Excel/CSV file (test 27th.csv)",
        type=['xlsx', 'xls', 'csv'],
        help="Upload your Excel or CSV file (.xlsx, .xls, or .csv format)"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        # Load and process data
        df = load_and_process_data(uploaded_file)
        
        if df is not None:
            # Display basic info
            st.success(f"✅ Successfully loaded {len(df):,} rows and {len(df.columns)} columns")
            
            # Show data preview
            st.markdown("## 📋 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Show column names for reference
            st.markdown("### 📝 Available Columns")
            st.write("Columns in your dataset:", list(df.columns))
            
            # Filters Section
            st.markdown("## 🔍 Filters")
            st.markdown('<div class="filter-section">', unsafe_allow_html=True)
            
            # Origin Type Filter
            if 'origintype' in df.columns:
                origin_types = ['All'] + list(df['origintype'].dropna().unique())
                selected_origin = st.selectbox("Filter by Origin Type:", origin_types)
                
                if selected_origin != 'All':
                    df_filtered = df[df['origintype'] == selected_origin]
                else:
                    df_filtered = df
            else:
                df_filtered = df
                st.info("No 'origintype' column found in the data")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Overall Metrics
            st.markdown("## 📈 Overall Delivery Metrics")
            metrics = calculate_delivery_metrics(df_filtered)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Total Requests</h3>
                    <h2>{metrics['total_requests']:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Sent</h3>
                    <h2>{metrics['total_sent']:,.0f}</h2>
                    <p>{metrics['sent_percentage']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Delivered</h3>
                    <h2>{metrics['total_delivered']:,.0f}</h2>
                    <p>{metrics['delivered_percentage']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Submitted</h3>
                    <h2>{metrics['total_submitted']:,.0f}</h2>
                    <p>{metrics['submitted_percentage']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Additional Metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Failed</h3>
                    <h2>{metrics['total_failed']:,.0f}</h2>
                    <p>{metrics['failed_percentage']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Pending</h3>
                    <h2>{metrics['total_pending']:,.0f}</h2>
                    <p>{metrics['pending_percentage']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Not Sent</h3>
                    <h2>{metrics['total_not_sent']:,.0f}</h2>
                    <p>{metrics['not_sent_percentage']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Pricing Model Analysis
            st.markdown("## 💰 Pricing Model Analysis")
            pricing_analysis = analyze_pricing_model_metrics(df_filtered)
            
            if not pricing_analysis.empty:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.dataframe(pricing_analysis, use_container_width=True)
                
                # Pricing model chart
                fig_pricing = px.bar(
                    pricing_analysis,
                    x='pricingmodel',
                    y=['sentcount', 'deliveredcount', 'submittedcount'],
                    title="Pricing Model Performance",
                    barmode='group'
                )
                st.plotly_chart(fig_pricing, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No pricing model data available")
            
            # Country Analysis
            st.markdown("## 🌍 Country-wise Analysis")
            country_analysis = analyze_country_metrics(df_filtered)
            
            if not country_analysis.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.dataframe(country_analysis.head(15), use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    # Country delivery chart
                    fig_country = px.bar(
                        country_analysis.head(15),
                        x='country',
                        y='delivered_percentage',
                        title="Top 15 Countries by Delivery Percentage"
                    )
                    st.plotly_chart(fig_country, use_container_width=True)
            else:
                st.info("No country data available")
            
            # Account Failure Analysis
            st.markdown("## ❌ Account Failure Analysis")
            account_failures = analyze_account_failures(df_filtered)
            
            if not account_failures.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.dataframe(account_failures.head(10), use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    # Account failure chart
                    fig_account = px.bar(
                        account_failures.head(10),
                        x='accountid',
                        y='failure_rate',
                        title="Top 10 Accounts by Failure Rate"
                    )
                    st.plotly_chart(fig_account, use_container_width=True)
            else:
                st.info("No account ID data available")
            
            # Template Failure Analysis
            st.markdown("## 📧 Template Failure Analysis")
            template_failures = analyze_template_failures(df_filtered)
            
            if not template_failures.empty:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.dataframe(template_failures.head(10), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No template data available")
            
            # Pricing Delivery Table
            st.markdown("## 📊 Pricing Model Delivery Table")
            pricing_delivery = analyze_pricing_delivery_table(df_filtered)
            
            if not pricing_delivery.empty:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.dataframe(pricing_delivery, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No pricing model data available")
            
            # Export Options
            st.markdown("## 💾 Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Export to CSV
                csv = df_filtered.to_csv(index=False)
                st.download_button(
                    label="📄 Download Filtered Data as CSV",
                    data=csv,
                    file_name=f"filtered_analysis_{uploaded_file.name.split('.')[0]}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Export analysis summary
                summary_data = {
                    'Metric': ['Total Requests', 'Sent', 'Delivered', 'Submitted', 'Failed', 'Pending', 'Not Sent'],
                    'Count': [metrics['total_requests'], metrics['total_sent'], metrics['total_delivered'], 
                             metrics['total_submitted'], metrics['total_failed'], metrics['total_pending'], metrics['total_not_sent']],
                    'Percentage': [100, metrics['sent_percentage'], metrics['delivered_percentage'], 
                                  metrics['submitted_percentage'], metrics['failed_percentage'], metrics['pending_percentage'], metrics['not_sent_percentage']]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_csv = summary_df.to_csv(index=False)
                st.download_button(
                    label="📊 Download Analysis Summary",
                    data=summary_csv,
                    file_name=f"analysis_summary_{uploaded_file.name.split('.')[0]}.csv",
                    mime="text/csv"
                )
            
        else:
            st.error("Failed to load the file. Please check the file format.")
    
    else:
        # Show expected data structure
        st.markdown("## 📝 Expected Data Structure")
        st.markdown("""
        Your Excel/CSV file should contain columns like:
        
        | as_of_date | accountid | tmplid | tmplname | country | origintype | pricingtype | pricingmodel | requestedcount | submittedcount | sentcount | deliveredcount | failedcount | pendingcount | notsentcount |
        |------------|-----------|--------|----------|---------|------------|-------------|--------------|----------------|----------------|----------|----------------|------------|--------------|--------------|
        | July 25, 2025 | 2000205432 | 7125860 | otp_traffic_free | Australia | authentication | NA | PMP | 137 | 137 | 0 | 0 | 137 | 0 | 0 |
        
        **Required columns for full analysis:**
        - accountid, tmplid, tmplname, country, origintype, pricingmodel
        - requestedcount, submittedcount, sentcount, deliveredcount, failedcount, pendingcount, notsentcount
        """)

if __name__ == "__main__":
    main() 