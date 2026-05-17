import pandas as pd
import numpy as np
from ETL_Pipeline import OlistETLPipeline
# ==========================================
# step1 / Read final gold file (global)
# ==========================================

pipeline = OlistETLPipeline()

final_gold_file = pipeline.build()

# RFM is calculated once at startup and reused by generate_business_insights
def _build_rfm():
    df = final_gold_file.copy()
    last_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

    RFM = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (last_date - x.max()).days,
        'order_id': 'nunique',
        'payment_value': 'sum'
    })
    RFM.rename(columns={
        'order_purchase_timestamp': 'Recency',
        'order_id': 'Frequency',
        'payment_value': 'Monetary'
    }, inplace=True)

    RFM['R_Score'] = pd.qcut(RFM['Recency'], 5, labels=[5, 4, 3, 2, 1])
    RFM['F_Score'] = pd.qcut(RFM['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    RFM['M_Score'] = pd.qcut(RFM['Monetary'], 5, labels=[1, 2, 3, 4, 5])

    RFM['R_Score'] = RFM['R_Score'].astype(int)
    RFM['F_Score'] = RFM['F_Score'].astype(int)
    RFM['M_Score'] = RFM['M_Score'].astype(int)

    def segment_customer(row):
        R, F, M = row['R_Score'], row['F_Score'], row['M_Score']
        if R >= 4 and F >= 4 and M >= 4:
            return "Champions"
        elif R >= 3 and F >= 3:
            return "Loyal-customer"
        elif R >= 4 and F <= 2:
            return "New-customer"
        elif R <= 2 and F >= 4:
            return "At-Risk"
        elif R <= 2 and F <= 2:
            return "Churned"
        else:
            return "Other"

    RFM['Segment'] = RFM.apply(segment_customer, axis=1)
    RFM['RFM_Score'] = RFM['R_Score'].astype(str) + RFM['F_Score'].astype(str) + RFM['M_Score'].astype(str)
    return RFM

# Build RFM once at import time
_rfm_df = _build_rfm()


##=========================================================
## Tool 1: Analyze sales revenue over a given date range
##=========================================================

def get_revenue_by_range(start_date: str, end_date: str):
    """Calculates total revenue between two dates. Format: YYYY-MM-DD."""
    start = pd.to_datetime(start_date)
    end   = pd.to_datetime(end_date)

    mask = (
        (final_gold_file['order_purchase_timestamp'] >= start) &
        (final_gold_file['order_purchase_timestamp'] <= end)
    )
    total_revenue = final_gold_file.loc[mask, 'payment_value'].sum()
    return f"Total revenue from {start_date} to {end_date} is: ${total_revenue:,.2f}"


##=========================================================
## Tool 2: Return top-selling products for a given period
##=========================================================

def Top_selling_products(start_of_period: str, end_of_period: str):
    """Identifies the best-selling product category and its revenue for a given period."""
    start = pd.to_datetime(start_of_period)
    end   = pd.to_datetime(end_of_period)

    mask = (
        (final_gold_file['order_purchase_timestamp'] >= start) &
        (final_gold_file['order_purchase_timestamp'] <= end)
    )
    filtered = final_gold_file.loc[mask]

    top_cat = filtered['product_category_name_english'].value_counts().idxmax()
    revenue = filtered.loc[
        filtered['product_category_name_english'] == top_cat, 'payment_value'
    ].sum()

    return (
        f"Top selling category from {start_of_period} to {end_of_period} "
        f"is: ({top_cat}) with total revenue: ${revenue:,.2f}"
    )


##=========================================================
## Tool 3: Detect anomalies (sudden spikes) in revenue
##=========================================================

def Detect_sales_anomalies(target_date: str):
    """
    Checks if a specific date had unusually high sales compared to the historical average.
    target_date format: YYYY-MM-DD
    """
    df = final_gold_file.copy()
    df['pure_date'] = df['order_purchase_timestamp'].dt.date
    target = pd.to_datetime(target_date).date()

    daily_sales = df.groupby('pure_date')['payment_value'].sum()

    mean_sales  = daily_sales.mean()
    std_sales   = daily_sales.std()
    upper_limit = mean_sales + (2 * std_sales)

    if target not in daily_sales.index:
        return "Date not found in the dataset."

    current_sales = daily_sales[target]

    if current_sales > upper_limit:
        day_data = df[df['pure_date'] == target]
        top_cat  = day_data['product_category_name_english'].value_counts().idxmax()
        return (
            f"Spike Detected! Sales on {target_date} (${current_sales:,.0f}) are significantly "
            f"higher than the usual limit (${upper_limit:,.0f}). "
            f"Main driver: high demand on '{top_cat}'."
        )
    else:
        return f"Normal day. Sales on {target_date} (${current_sales:,.0f}) are within limits."


##=========================================================
## Tool 4: Generate business insights from customer segments
##=========================================================

def generate_business_insights():
    """
    Provides a high-level summary of customer segments (Champions, Loyal, At-Risk, etc.)
    based on RFM analysis. Use this to answer questions about customer behaviour or loyalty.
    """
    insights = _rfm_df.groupby('Segment').agg(
        Avg_Recency=('Recency', 'mean'),
        Avg_Frequency=('Frequency', 'mean'),
        Avg_Monetary=('Monetary', 'mean'),
        Total_Revenue=('Monetary', 'sum'),
        Customer_Count=('Monetary', 'count')
    ).round(2)

    total_rev = insights['Total_Revenue'].sum()
    insights['Revenue_Contribution_%'] = (
        (insights['Total_Revenue'] / total_rev) * 100
    ).round(2)

    result = insights.sort_values('Total_Revenue', ascending=False)
    return result.to_string()


##=========================================================
## Tool 5: Compare two time periods side by side
##=========================================================

def compare_periods(
    current_start: str, current_end: str,
    previous_start: str, previous_end: str
):
    """
    Compares business performance (Revenue, Orders, Customers, Avg Order Value)
    between two time periods and shows growth %.
    All dates format: YYYY-MM-DD.
    """
    df = final_gold_file.copy()
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

    current_period  = df[(df['order_purchase_timestamp'] >= current_start)  & (df['order_purchase_timestamp'] <= current_end)]
    previous_period = df[(df['order_purchase_timestamp'] >= previous_start) & (df['order_purchase_timestamp'] <= previous_end)]

    def summary(data):
        orders = data['order_id'].nunique()
        return pd.Series({
            'Revenue':data['payment_value'].sum(),
            'Orders':orders,
            'Customers':data['customer_unique_id'].nunique(),
            'Avg_Order_Value':data['payment_value'].sum() / orders if orders > 0 else 0
        })

    comparison = pd.DataFrame({
        'Previous Period': summary(previous_period),
        'Current Period':  summary(current_period)
    })
    comparison['Growth_%'] = (
        (comparison['Current Period'] - comparison['Previous Period']) /
        comparison['Previous Period'] * 100
    ).round(2)

    return comparison.to_string()

##=========================================================
## Tool 6: Analyze monthly trends and category performance
##=========================================================

def analyze_sales_performance():
    """
    Analyzes monthly revenue trends, calculates growth %, and compares category performance.
    Use this for: Seasonal trends, Category comparisons, and finding root causes of drops.
    """
    df = final_gold_file.copy()
    df['month_period'] = pd.to_datetime(df['order_purchase_timestamp']).dt.to_period('M')
    
    
    # A. Monthly Trends 
    monthly_analyze = df.groupby('month_period').agg(
        Monthly_Revenue=('payment_value', 'sum'),
        Order_Count=('order_id', 'nunique')
    ).reset_index()
    
    monthly_analyze['Growth_%'] = (monthly_analyze['Monthly_Revenue'].pct_change()*100).round(2)
    
    
    # B. Category Performance 
    valid_growth = monthly_analyze.dropna(subset=['Growth_%'])
    if valid_growth.empty:
        return "Not enough historical data to perform trend analysis."
     
    worst_month_idx = valid_growth['Growth_%'].idxmin()
    
    # C. drop analysis 
    month_of_drop = monthly_analyze.loc[worst_month_idx, 'month_period']
    month_before_drop = monthly_analyze.loc[worst_month_idx - 1, 'month_period']
    drop_val = monthly_analyze.loc[worst_month_idx, 'Growth_%']


    # D. (Root-Cause Detection)
    target_months = [month_before_drop, month_of_drop]
    cat_comparison = df[df['month_period'].isin(target_months)].groupby(
        ['month_period', 'product_category_name_english']
    )['payment_value'].sum().unstack(level=0).fillna(0)
    
    #Calculate the difference between month_of_drop and the month before it
    cat_comparison['Revenue_Diff'] = cat_comparison[month_of_drop] - cat_comparison[month_before_drop]
    
    #category dropping
    top_losers = cat_comparison.sort_values('Revenue_Diff', ascending=True).head(3)
    # top sales in month_of_drop
    top_gainers = cat_comparison.sort_values('Revenue_Diff', ascending=False).head(3)

    
    report = (
        f"--- 📈 General Monthly Trend ---\n"
        f"{monthly_analyze.tail(5).to_string(index=False)}\n\n"
        f"--- 🚨 Critical Anomaly Detected ---\n"
        f"Sharpest drop identified in {month_of_drop} ({drop_val}% compared to {month_before_drop}).\n\n"
        f"--- 🔍 Root-Cause Analysis (Why did it happen?) ---\n"
        f"Top categories responsible for the revenue loss in {month_of_drop}:\n"
        f"{top_losers['Revenue_Diff'].to_string()}\n\n"
        f"Top performing categories that resisted the drop:\n"
        f"{top_gainers['Revenue_Diff'].to_string()}"
    )
    
    return report


##=========================================================
## Tool 7: analyze_marketing_efficiency
##=========================================================
def analyze_marketing_efficiency():
    """
    Calculates ROAS (Return on Ads Spend) by merging sales data with marketing spend.
    """
    sales_df = final_gold_file.copy()
    sales_df['month_period'] = sales_df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    monthly_sales = sales_df.groupby('month_period')['payment_value'].sum().reset_index()

    # 1. reading the marketing spending file  
    try:
        marketing_df = pd.read_csv('marketing_spend.csv')
    except FileNotFoundError:
        return "Error: marketing_spend.csv file not found. Please generate it first."

    # 2.Monthly Marketing spending
    monthly_spend = marketing_df.groupby('month_period')['spend'].sum().reset_index()

    # 3.Merge (spending money & revenue)
    performance_df = pd.merge(monthly_sales, monthly_spend, on='month_period', how='inner')

    # 4.calculate (ROAS)
    performance_df['ROAS'] = (performance_df['payment_value'] / performance_df['spend']).round(2)
    
    # worst month ( spending money is more than Revenue )
    worst_month = performance_df.loc[performance_df['ROAS'].idxmin()]
    
    # best month ( Revenue is more more than spending money )
    best_month = performance_df.loc[performance_df['ROAS'].idxmax()]

    # 5.spending Report 
    report = (
        f"--- Global Marketing Performance Analysis ---\n"
        f"Total Months Analyzed: {len(performance_df)}\n"
        f"Average ROAS: {performance_df['ROAS'].mean():.2f}x\n\n"
        
        f"---  Critical Marketing Inefficiency (Worst Month) ---\n"
        f"Month: {worst_month['month_period']}\n"
        f"Spend: ${worst_month['spend']:,} | Revenue: ${worst_month['payment_value']:,}\n"
        f"ROAS: {worst_month['ROAS']}x (This month had the lowest return on investment!)\n\n"
        
        f"---  Marketing Star (Best Month) ---\n"
        f"Month: {best_month['month_period']}\n"
        f"Spend: ${best_month['spend']:,} | Revenue: ${best_month['payment_value']:,}\n"
        f"ROAS: {best_month['ROAS']}x (This was your most efficient month!)\n\n"
        
        f"---  Recent 3-Month Trend ---\n"
        f"{performance_df.tail(3)[['month_period', 'spend', 'payment_value', 'ROAS']].to_string(index=False)}"
    )
    
    return report

##=========================================================
## Tool 8: analyze_customer_loyalty
##=======================================================

def analyze_customer_loyalty():
    """
    Analyzes customer retention, LTV, and repeat purchase behavior.
    """
    df = final_gold_file.copy()
    
    # 1.calculate customer lifetime value
    customer_stats = df.groupby('customer_unique_id').agg(
        total_spent=('payment_value', 'sum'),
        order_count=('order_id', 'nunique')
    ).reset_index()
    
    # 2. calcutale total customer & repeated customers
    total_customers = len(customer_stats)
    repeat_customers_df = customer_stats[customer_stats['order_count'] > 1]
    num_repeat_customers = len(repeat_customers_df)
    
    # calculate Retention Rate
    retention_rate = (num_repeat_customers / total_customers) * 100
    
    # average of customer lifetime value (LTV)
    avg_ltv = customer_stats['total_spent'].mean()

    # Calculate the customer Acquisition cost (CAC)
    try:
        marketing_spending_df = pd.read_csv('marketing_spend.csv')
        total_spend = marketing_spending_df['spend'].sum()
        # CAC Calculation
        avg_cac = total_spend / total_customers
    except:
        avg_cac = 0
    
    # 3. Reporting
    report = (
        f"### Advanced Customer & Marketing ROI Analysis\n"
        f"Total Unique Customers: {total_customers:,}\n"
        f"Retention Rate: {retention_rate:.2f}%\n\n"
        
        f"--- Unit Economics (LTV vs CAC) ---\n"
        f"Average LTV: ${avg_ltv:.2f} (What we earn from a customer)\n"
        f"Average CAC: ${avg_cac:.2f} (What we spend to get a customer)\n"
    )

    # 4. The Golden Ratio
    if avg_cac > 0:
        ratio = avg_ltv / avg_cac
        report += f"LTV/CAC Ratio: {ratio:.2f}x\n\n"
        
        if ratio < 1:
            report += " **Danger:** Your CAC is higher than your LTV! You are losing money on every new customer acquired."
        elif ratio < 3:
            report += " **Warning:** Your profit margin is thin. You need to improve retention or lower acquisition costs."
        else:
            report += " **Healthy:** Your business model is strong. You earn much more than you spend to acquire customers."
            
    return report

##=========================================================
## Tool 9: get_business_health_check
##=======================================================
def get_business_health_check():
    """
    Automated Insights Engine: Proactively detects anomalies across Sales, 
    Marketing, and Customers, providing data-driven prompts for the AI to analyze.
    """
    # 1.Sales Scan
    df = final_gold_file.copy()
    df['month_period'] = df['order_purchase_timestamp'].dt.to_period('M')
    
    # calculate monthly sales and change percentage %
    monthly_sales = df.groupby('month_period')['payment_value'].sum()
    monthly_growth = monthly_sales.pct_change()
    
    # select the last month growth & Total sales of this month
    last_growth = monthly_growth.iloc[-1]
    last_month_value = monthly_sales.iloc[-1]

    # 2.Marketing Scan
    try:
        mkt_df = pd.read_csv('marketing_spend.csv')
        mkt_df['month_period'] = pd.to_period(mkt_df['month_period'], freq='M')
        
        last_month_idx = monthly_sales.index[-1]
        last_month_spend = mkt_df[mkt_df['month_period'] == last_month_idx]['spend'].sum()
        
        # calculate (ROAS)
        last_roas = last_month_value / last_month_spend if last_month_spend > 0 else 0
    except:
        last_roas = 0
        last_month_spend = 0

    # 3. Customer Scan
    customer_stats = df.groupby('customer_unique_id').agg(
        order_count=('order_id', 'nunique')
    )
    total_customers = len(customer_stats)
    repeat_customers = len(customer_stats[customer_stats['order_count'] > 1])
    retention_rate = (repeat_customers / total_customers) * 100 if total_customers > 0 else 0

    # 4. Alerts Templete
    alerts = []
    # AI recommendations guidelines
    ai_guidelines = []

    # -- sales Drop scanning--
    if last_growth < -0.10:
        alerts.append(f"🚨 [CRITICAL] Sales dropped by {abs(last_growth)*100:.1f}% this month.")
        ai_guidelines.append("ANALYZE_SALES_DROP: Evaluate potential causes like seasonal shifts, category-specific declines, or external market factors.")

    # -- Marketing Ads quality --
    if last_roas < 3.0 and last_month_spend > 0:
        alerts.append(f"⚠️ [WARNING] Low ROAS detected ({last_roas:.2f}x).")
        ai_guidelines.append("OPTIMIZE_MARKETING: Suggest how to improve ad efficiency, focusing on high-performing products vs. wasteful spending.")

    # -- customer retention rate scanning--
    if retention_rate < 5:
        alerts.append(f"📢 [INSIGHT] Very low Retention Rate: {retention_rate:.2f}%.")
        ai_guidelines.append("INVESTIGATE_RETENTION: Most customers buy only once. Analyze multiple root causes: Is it a product quality issue, slow shipping, poor customer service, or high pricing compared to competitors?")

    # 5. The Data-Driven Summary
    report = "### ⚡ Automated Business Health Check\n"
    report += f"**Latest Status:** Sales Growth: {last_growth*100:.1f}% | ROAS: {last_roas:.2f}x | Retention: {retention_rate:.2f}%\n\n"
    
    report += "**Detected Anomalies:**\n" + ("\n".join(alerts) if alerts else "✅ No critical alerts detected.") + "\n\n"
    
    report += "**AI Strategic Analysis Brief:**\n"
    if ai_guidelines:
        report += "Tommy, please use your intelligence to analyze the following signals and provide holistic business advice:\n"
        report += "\n".join([f"- {g}" for g in ai_guidelines])
    else:
        report += "All metrics are within healthy ranges. Suggest ways to scale the current success."

    return report

##=========================================================
## Tool 10:get_quick_alerts
##=======================================================

def get_quick_alerts():
    """
    A lightweight version of the health check to be used as a 'startup notification'.
    """
    report = get_business_health_check()
    lines = report.split('\n')
    important_alerts = [l for l in lines if "🚨" in l or "⚠️" in l or "📢" in l]
    
    if important_alerts:
        return "⚠️ QUICK ALERT: I've detected some issues in your latest data:\n" + "\n".join(important_alerts)
    return "✅ Everything looks stable today! Ready for your questions."