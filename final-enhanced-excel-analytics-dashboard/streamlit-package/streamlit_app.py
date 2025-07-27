import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
import base64

# Page configuration
st.set_page_config(
    page_title="Excel Analytics Dashboard",
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
</style>
""", unsafe_allow_html=True)

def calculate_numeric_stats(df, column):
    """Calculate comprehensive statistics for numeric columns"""
    stats = {
        'count': df[column].count(),
        'mean': df[column].mean(),
        'median': df[column].median(),
        'std': df[column].std(),
        'min': df[column].min(),
        'max': df[column].max(),
        'sum': df[column].sum(),
        'range': df[column].max() - df[column].min(),
        'q25': df[column].quantile(0.25),
        'q75': df[column].quantile(0.75)
    }
    return stats

def calculate_categorical_stats(df, column):
    """Calculate statistics for categorical columns"""
    value_counts = df[column].value_counts()
    stats = {
        'count': df[column].count(),
        'unique': df[column].nunique(),
        'most_common': value_counts.index[0] if len(value_counts) > 0 else 'N/A',
        'most_common_count': value_counts.iloc[0] if len(value_counts) > 0 else 0,
        'top_values': value_counts.head(10).to_dict()
    }
    return stats

def create_histogram(df, column):
    """Create histogram for numeric data"""
    fig = px.histogram(
        df, 
        x=column, 
        nbins=20,
        title=f"Distribution of {column}",
        labels={column: column, 'count': 'Frequency'}
    )
    fig.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_bar_chart(df, column):
    """Create bar chart for categorical data"""
    value_counts = df[column].value_counts().head(10)
    fig = px.bar(
        x=value_counts.index,
        y=value_counts.values,
        title=f"Top 10 Values in {column}",
        labels={'x': column, 'y': 'Count'}
    )
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_box_plot(df, column):
    """Create box plot for numeric data"""
    fig = px.box(
        df, 
        y=column,
        title=f"Box Plot of {column}"
    )
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_correlation_heatmap(df):
    """Create correlation heatmap for numeric columns"""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return None
    
    corr_matrix = numeric_df.corr()
    fig = px.imshow(
        corr_matrix,
        title="Correlation Heatmap",
        color_continuous_scale='RdBu',
        aspect="auto"
    )
    fig.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Excel Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Upload your Excel file to generate comprehensive analytics and insights for customer meetings</p>', unsafe_allow_html=True)
    
    # File upload
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload your Excel file (.xlsx or .xls format)"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        try:
            # Read the Excel file
            df = pd.read_excel(uploaded_file)
            
            # Display basic info
            st.success(f"✅ Successfully loaded {len(df)} rows and {len(df.columns)} columns")
            
            # Summary Statistics Section
            st.markdown("## 📈 Summary Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Total Records</h3>
                    <h2>{len(df):,}</h2>
                    <p>Number of data rows</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Total Columns</h3>
                    <h2>{len(df.columns)}</h2>
                    <p>Number of data columns</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Numeric Columns</h3>
                    <h2>{len(numeric_cols)}</h2>
                    <p>Columns with numeric data</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                completeness = (df.count().sum() / (len(df) * len(df.columns)) * 100)
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Data Quality</h3>
                    <h2>{completeness:.1f}%</h2>
                    <p>Data completeness score</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Data Preview
            st.markdown("## 📋 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Column Analysis Section
            st.markdown("## 🔍 Column Analysis")
            
            # Column selector
            selected_column = st.selectbox(
                "Select a column for detailed analysis:",
                df.columns.tolist(),
                index=0
            )
            
            if selected_column:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Column Information")
                    
                    # Check if numeric or categorical
                    if df[selected_column].dtype in ['int64', 'float64']:
                        stats = calculate_numeric_stats(df, selected_column)
                        
                        st.markdown(f"""
                        **Column Type:** Numeric  
                        **Data Type:** {df[selected_column].dtype}  
                        **Total Count:** {stats['count']:,}  
                        **Unique Values:** {df[selected_column].nunique():,}
                        """)
                        
                        # Numeric statistics
                        st.markdown("#### Statistical Measures")
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            st.metric("Mean", f"{stats['mean']:.2f}")
                            st.metric("Median", f"{stats['median']:.2f}")
                            st.metric("Standard Deviation", f"{stats['std']:.2f}")
                            st.metric("Sum", f"{stats['sum']:,.2f}")
                        
                        with col_b:
                            st.metric("Minimum", f"{stats['min']:.2f}")
                            st.metric("Maximum", f"{stats['max']:.2f}")
                            st.metric("Range", f"{stats['range']:.2f}")
                            st.metric("Q1", f"{stats['q25']:.2f}")
                            st.metric("Q3", f"{stats['q75']:.2f}")
                        
                        # Histogram
                        st.markdown("#### Distribution")
                        fig_hist = create_histogram(df, selected_column)
                        st.plotly_chart(fig_hist, use_container_width=True)
                        
                        # Box plot
                        st.markdown("#### Box Plot")
                        fig_box = create_box_plot(df, selected_column)
                        st.plotly_chart(fig_box, use_container_width=True)
                        
                    else:
                        stats = calculate_categorical_stats(df, selected_column)
                        
                        st.markdown(f"""
                        **Column Type:** Categorical  
                        **Data Type:** {df[selected_column].dtype}  
                        **Total Count:** {stats['count']:,}  
                        **Unique Values:** {stats['unique']:,}
                        """)
                        
                        # Categorical statistics
                        st.markdown("#### Top Values")
                        for value, count in list(stats['top_values'].items())[:5]:
                            percentage = (count / stats['count']) * 100
                            st.markdown(f"**{value}:** {count:,} ({percentage:.1f}%)")
                        
                        # Bar chart
                        st.markdown("#### Frequency Distribution")
                        fig_bar = create_bar_chart(df, selected_column)
                        st.plotly_chart(fig_bar, use_container_width=True)
                
                with col2:
                    st.markdown("### Data Quality Check")
                    
                    # Missing values
                    missing_count = df[selected_column].isnull().sum()
                    missing_percentage = (missing_count / len(df)) * 100
                    
                    st.markdown(f"""
                    **Missing Values:** {missing_count:,} ({missing_percentage:.1f}%)  
                    **Valid Values:** {stats['count']:,} ({100-missing_percentage:.1f}%)
                    """)
                    
                    # Data quality visualization
                    if missing_count > 0:
                        fig_missing = go.Figure(data=[
                            go.Pie(
                                labels=['Valid Values', 'Missing Values'],
                                values=[stats['count'], missing_count],
                                hole=0.4
                            )
                        ])
                        fig_missing.update_layout(
                            title="Data Completeness",
                            height=300,
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        st.plotly_chart(fig_missing, use_container_width=True)
            
            # Correlation Analysis (for numeric columns)
            if len(numeric_cols) >= 2:
                st.markdown("## 🔗 Correlation Analysis")
                fig_corr = create_correlation_heatmap(df)
                if fig_corr:
                    st.plotly_chart(fig_corr, use_container_width=True)
            
            # Data Export
            st.markdown("## 💾 Export Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Export to CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📄 Download as CSV",
                    data=csv,
                    file_name=f"analyzed_data_{uploaded_file.name.split('.')[0]}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Export to Excel
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Data', index=False)
                    
                    # Add summary sheet
                    summary_data = []
                    for col in df.columns:
                        if df[col].dtype in ['int64', 'float64']:
                            stats = calculate_numeric_stats(df, col)
                            summary_data.append({
                                'Column': col,
                                'Type': 'Numeric',
                                'Count': stats['count'],
                                'Mean': stats['mean'],
                                'Median': stats['median'],
                                'Std': stats['std'],
                                'Min': stats['min'],
                                'Max': stats['max']
                            })
                        else:
                            stats = calculate_categorical_stats(df, col)
                            summary_data.append({
                                'Column': col,
                                'Type': 'Categorical',
                                'Count': stats['count'],
                                'Unique': stats['unique'],
                                'Most Common': stats['most_common'],
                                'Most Common Count': stats['most_common_count']
                            })
                    
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                st.download_button(
                    label="📊 Download as Excel",
                    data=output.getvalue(),
                    file_name=f"analyzed_data_{uploaded_file.name.split('.')[0]}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col3:
                # Generate report
                st.button("📋 Generate Report", help="Coming soon: Generate a comprehensive PDF report")
            
        except Exception as e:
            st.error(f"Error reading the file: {str(e)}")
            st.info("Please make sure your Excel file is valid and contains data in the first sheet.")
    
    else:
        # Show sample data structure
        st.markdown("## 📝 Sample Data Structure")
        st.markdown("""
        Create an Excel file with the following structure to test the dashboard:
        
        ### Sales Data Example
        | Customer | Product | Sales | Quantity | Date | Region |
        |----------|---------|-------|----------|------|--------|
        | John Doe | Laptop | 1200 | 2 | 2024-01-15 | North |
        | Jane Smith | Mouse | 50 | 5 | 2024-01-16 | South |
        | Bob Johnson | Keyboard | 150 | 3 | 2024-01-17 | East |
        
        ### Customer Data Example
        | CustomerID | Name | Age | City | Income | PurchaseCount |
        |------------|------|-----|------|--------|---------------|
        | 1 | John Smith | 35 | New York | 75000 | 12 |
        | 2 | Sarah Johnson | 28 | Los Angeles | 65000 | 8 |
        | 3 | Michael Brown | 42 | Chicago | 85000 | 15 |
        """)

if __name__ == "__main__":
    main() 