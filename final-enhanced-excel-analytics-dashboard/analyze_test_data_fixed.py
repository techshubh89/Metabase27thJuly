import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def load_and_analyze_data():
    """Load and analyze the test 27th.csv file"""
    
    # Load the data
    print("📊 Loading data from 'test 27th.csv'...")
    df = pd.read_csv('test 27th.csv')
    
    # Convert numeric columns to proper types
    numeric_columns = ['requestedcount', 'submittedcount', 'sentcount', 'deliveredcount', 
                      'readcount', 'failedcount', 'notsentcount']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    print(f"✅ Data loaded successfully!")
    print(f"📈 Total records: {len(df):,}")
    print(f"📋 Total columns: {len(df.columns)}")
    print(f"📅 Date range: {df['as_of_date'].min()} to {df['as_of_date'].max()}")
    
    # Display column names
    print(f"\n📝 Available columns:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    # Basic data info
    print(f"\n🔍 Data Overview:")
    print(df.info())
    
    return df

def analyze_origin_type_filter(df):
    """1. Filter as per Origin type"""
    print(f"\n{'='*60}")
    print("1. 🔍 ORIGIN TYPE ANALYSIS")
    print(f"{'='*60}")
    
    origin_counts = df['origintype'].value_counts()
    print(f"Origin Types found:")
    for origin, count in origin_counts.items():
        print(f"  • {origin}: {count:,} records ({count/len(df)*100:.1f}%)")
    
    return origin_counts

def analyze_pricing_model_metrics(df):
    """2. Pricing model wise metrics"""
    print(f"\n{'='*60}")
    print("2. 💰 PRICING MODEL ANALYSIS")
    print(f"{'='*60}")
    
    pricing_analysis = df.groupby('pricingmodel').agg({
        'sentcount': 'sum',
        'deliveredcount': 'sum',
        'requestedcount': 'sum',
        'submittedcount': 'sum'
    }).reset_index()
    
    # Calculate percentages
    pricing_analysis['sent_percentage'] = (pricing_analysis['sentcount'] / pricing_analysis['requestedcount']) * 100
    pricing_analysis['delivered_percentage'] = (pricing_analysis['deliveredcount'] / pricing_analysis['requestedcount']) * 100
    pricing_analysis['submitted_percentage'] = (pricing_analysis['submittedcount'] / pricing_analysis['requestedcount']) * 100
    
    print("Pricing Model Performance:")
    print(pricing_analysis.to_string(index=False, float_format='%.2f'))
    
    return pricing_analysis

def analyze_pending_and_not_sent(df):
    """3 & 4. Pending and Not sent analysis"""
    print(f"\n{'='*60}")
    print("3 & 4. ⏳ PENDING & NOT SENT ANALYSIS")
    print(f"{'='*60}")
    
    total_requested = df['requestedcount'].sum()
    total_pending = df['pendingcount'].sum()
    total_not_sent = df['notsentcount'].sum()
    
    print(f"📊 Overall Metrics:")
    print(f"  • Total Requested: {total_requested:,}")
    print(f"  • Total Pending: {total_pending:,} ({total_pending/total_requested*100:.2f}%)")
    print(f"  • Total Not Sent: {total_not_sent:,} ({total_not_sent/total_requested*100:.2f}%)")
    
    # By pricing model
    pending_by_model = df.groupby('pricingmodel').agg({
        'pendingcount': 'sum',
        'notsentcount': 'sum',
        'requestedcount': 'sum'
    }).reset_index()
    
    pending_by_model['pending_percentage'] = (pending_by_model['pendingcount'] / pending_by_model['requestedcount']) * 100
    pending_by_model['not_sent_percentage'] = (pending_by_model['notsentcount'] / pending_by_model['requestedcount']) * 100
    
    print(f"\n📈 By Pricing Model:")
    print(pending_by_model.to_string(index=False, float_format='%.2f'))
    
    return pending_by_model

def analyze_country_metrics(df):
    """5. Country wise delivery and submitted analysis"""
    print(f"\n{'='*60}")
    print("5. 🌍 COUNTRY-WISE ANALYSIS")
    print(f"{'='*60}")
    
    country_analysis = df.groupby('country').agg({
        'deliveredcount': 'sum',
        'submittedcount': 'sum',
        'requestedcount': 'sum'
    }).reset_index()
    
    country_analysis['delivered_percentage'] = (country_analysis['deliveredcount'] / country_analysis['requestedcount']) * 100
    country_analysis['submitted_percentage'] = (country_analysis['submittedcount'] / country_analysis['requestedcount']) * 100
    
    # Sort by delivered count
    country_analysis = country_analysis.sort_values('deliveredcount', ascending=False)
    
    print("Top 15 Countries by Delivery Count:")
    print(country_analysis.head(15).to_string(index=False, float_format='%.2f'))
    
    return country_analysis

def analyze_account_failures(df):
    """6. Account ID with highest failure analysis"""
    print(f"\n{'='*60}")
    print("6. ❌ ACCOUNT FAILURE ANALYSIS")
    print(f"{'='*60}")
    
    # Calculate failure rate for each account
    account_failures = df.groupby('accountid').agg({
        'failedcount': 'sum',
        'requestedcount': 'sum',
        'tmplid': 'nunique'  # Number of unique templates
    }).reset_index()
    
    account_failures['failure_rate'] = (account_failures['failedcount'] / account_failures['requestedcount']) * 100
    account_failures = account_failures.sort_values('failure_rate', ascending=False)
    
    print("Top 10 Accounts by Failure Rate:")
    print(account_failures.head(10).to_string(index=False, float_format='%.2f'))
    
    # Account with highest absolute failures
    highest_failures = account_failures.sort_values('failedcount', ascending=False).head(5)
    print(f"\n📊 Top 5 Accounts by Absolute Failure Count:")
    print(highest_failures.to_string(index=False, float_format='%.2f'))
    
    return account_failures

def analyze_template_failures(df):
    """7. Templates with maximum failure and their account IDs"""
    print(f"\n{'='*60}")
    print("7. 📧 TEMPLATE FAILURE ANALYSIS")
    print(f"{'='*60}")
    
    # Analyze by template
    template_failures = df.groupby(['tmplid', 'tmplname', 'accountid']).agg({
        'failedcount': 'sum',
        'requestedcount': 'sum'
    }).reset_index()
    
    template_failures['failure_rate'] = (template_failures['failedcount'] / template_failures['requestedcount']) * 100
    template_failures = template_failures.sort_values('failure_rate', ascending=False)
    
    print("Top 15 Templates by Failure Rate:")
    print(template_failures.head(15).to_string(index=False, float_format='%.2f'))
    
    # Templates with highest absolute failures
    highest_template_failures = template_failures.sort_values('failedcount', ascending=False).head(10)
    print(f"\n📊 Top 10 Templates by Absolute Failure Count:")
    print(highest_template_failures.to_string(index=False, float_format='%.2f'))
    
    return template_failures

def analyze_pricing_delivery_table(df):
    """8. Pricing model, pricing type and delivered table"""
    print(f"\n{'='*60}")
    print("8. 📊 PRICING MODEL DELIVERY TABLE")
    print(f"{'='*60}")
    
    pricing_delivery = df.groupby(['pricingmodel', 'pricingtype']).agg({
        'deliveredcount': 'sum',
        'requestedcount': 'sum'
    }).reset_index()
    
    pricing_delivery['delivery_rate'] = (pricing_delivery['deliveredcount'] / pricing_delivery['requestedcount']) * 100
    pricing_delivery = pricing_delivery.sort_values('delivery_rate', ascending=False)
    
    print("Pricing Model & Type Delivery Performance:")
    print(pricing_delivery.to_string(index=False, float_format='%.2f'))
    
    return pricing_delivery

def generate_summary_report(df):
    """Generate a comprehensive summary report"""
    print(f"\n{'='*60}")
    print("📋 COMPREHENSIVE SUMMARY REPORT")
    print(f"{'='*60}")
    
    # Overall metrics
    total_requested = df['requestedcount'].sum()
    total_submitted = df['submittedcount'].sum()
    total_sent = df['sentcount'].sum()
    total_delivered = df['deliveredcount'].sum()
    total_failed = df['failedcount'].sum()
    total_pending = df['pendingcount'].sum()
    total_not_sent = df['notsentcount'].sum()
    
    print(f"📈 OVERALL PERFORMANCE METRICS:")
    print(f"  • Total Requested: {total_requested:,}")
    print(f"  • Total Submitted: {total_submitted:,} ({total_submitted/total_requested*100:.2f}%)")
    print(f"  • Total Sent: {total_sent:,} ({total_sent/total_requested*100:.2f}%)")
    print(f"  • Total Delivered: {total_delivered:,} ({total_delivered/total_requested*100:.2f}%)")
    print(f"  • Total Failed: {total_failed:,} ({total_failed/total_requested*100:.2f}%)")
    print(f"  • Total Pending: {total_pending:,} ({total_pending/total_requested*100:.2f}%)")
    print(f"  • Total Not Sent: {total_not_sent:,} ({total_not_sent/total_requested*100:.2f}%)")
    
    # Key insights
    print(f"\n🔍 KEY INSIGHTS:")
    print(f"  • Success Rate (Delivered/Requested): {total_delivered/total_requested*100:.2f}%")
    print(f"  • Failure Rate: {total_failed/total_requested*100:.2f}%")
    print(f"  • Processing Rate (Sent/Requested): {total_sent/total_requested*100:.2f}%")
    
    # Top performers
    print(f"\n🏆 TOP PERFORMERS:")
    
    # Best performing country
    country_perf = df.groupby('country')['deliveredcount'].sum().sort_values(ascending=False)
    print(f"  • Top Country: {country_perf.index[0]} ({country_perf.iloc[0]:,} delivered)")
    
    # Best performing pricing model
    pricing_perf = df.groupby('pricingmodel')['deliveredcount'].sum().sort_values(ascending=False)
    print(f"  • Top Pricing Model: {pricing_perf.index[0]} ({pricing_perf.iloc[0]:,} delivered)")
    
    # Best performing origin type
    origin_perf = df.groupby('origintype')['deliveredcount'].sum().sort_values(ascending=False)
    print(f"  • Top Origin Type: {origin_perf.index[0]} ({origin_perf.iloc[0]:,} delivered)")

def main():
    """Main analysis function"""
    try:
        # Load data
        df = load_and_analyze_data()
        
        # Perform all analyses
        origin_analysis = analyze_origin_type_filter(df)
        pricing_analysis = analyze_pricing_model_metrics(df)
        pending_analysis = analyze_pending_and_not_sent(df)
        country_analysis = analyze_country_metrics(df)
        account_failures = analyze_account_failures(df)
        template_failures = analyze_template_failures(df)
        pricing_delivery = analyze_pricing_delivery_table(df)
        
        # Generate summary report
        generate_summary_report(df)
        
        print(f"\n{'='*60}")
        print("✅ ANALYSIS COMPLETE!")
        print(f"{'='*60}")
        print("📊 All requested metrics have been analyzed and displayed above.")
        print("💡 Use this enhanced Streamlit dashboard for interactive visualization.")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        print("Please check if the file 'test 27th.csv' is in the current directory.")

if __name__ == "__main__":
    main() 