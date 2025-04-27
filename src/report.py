"""
Module for generating financial analysis reports.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List
import yaml
from tabulate import tabulate
import shutil

def load_config() -> Dict:
    """Load configuration from config.yml."""
    with open("config.yml", "r") as f:
        return yaml.safe_load(f)

def load_processed_data() -> pd.DataFrame:
    """Load all processed transaction data."""
    processed_dir = Path("data/processed")
    dfs = []
    
    # Look for account-specific directories
    for account_dir in processed_dir.glob("account_*"):
        # Extract account number from directory name
        account_number = account_dir.name.split('_')[1]
        
        # Load transactions file
        transactions_file = account_dir / "transactions.csv"
        if transactions_file.exists():
            df = pd.read_csv(transactions_file)
            df['date'] = pd.to_datetime(df['date'])
            df['account_number'] = account_number
            dfs.append(df)
    
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def generate_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate monthly category summary pivot table for expenses only.
    
    Args:
        df: Processed transaction DataFrame
        
    Returns:
        DataFrame with months as rows and categories as columns, showing expenses only
    """
    # Filter for expenses only
    expenses = df[df['transaction_type'] == 'expense']
    
    # Create month column
    expenses['month'] = expenses['date'].dt.to_period('M')
    
    # Pivot table for expenses
    expense_pivot = pd.pivot_table(
        expenses,
        values='amount',
        index='month',
        columns='category',
        aggfunc='sum',
        fill_value=0
    )
    
    # Take absolute values since expenses are negative
    expense_pivot = expense_pivot.abs()
    
    return expense_pivot

def calculate_rolling_averages(df: pd.DataFrame, months: int = 4) -> pd.DataFrame:
    """
    Calculate rolling average spending by category for expenses only.
    
    Args:
        df: Processed transaction DataFrame
        months: Number of months to include in rolling average
        
    Returns:
        DataFrame with rolling averages by category for expenses
    """
    # Filter for expenses only
    expenses = df[df['transaction_type'] == 'expense']
    
    # Create month column
    expenses['month'] = expenses['date'].dt.to_period('M')
    
    # Calculate monthly totals (use absolute values for expenses)
    monthly_totals = expenses.groupby(['month', 'category'])['amount'].sum().abs().unstack()
    
    # Calculate rolling average
    rolling_avg = monthly_totals.rolling(window=months, min_periods=1).mean()
    
    return rolling_avg

def identify_top_merchants(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Identify top merchants by expense amount and frequency.
    
    Args:
        df: Processed transaction DataFrame
        n: Number of top merchants to return
        
    Returns:
        DataFrame with merchant expense statistics
    """
    # Filter for expenses only
    expenses = df[df['transaction_type'] == 'expense']
    
    # Group by merchant and calculate statistics
    merchant_stats = expenses.groupby('description').agg({
        'amount': ['count', 'sum', 'mean']
    }).reset_index()
    
    merchant_stats.columns = ['merchant', 'transaction_count', 'total_spent', 'average_transaction']
    
    # Take absolute values for easier reading
    merchant_stats['total_spent'] = merchant_stats['total_spent'].abs()
    merchant_stats['average_transaction'] = merchant_stats['average_transaction'].abs()
    
    # Sort by total spent
    merchant_stats = merchant_stats.sort_values('total_spent', ascending=False)
    
    return merchant_stats.head(n)

def flag_large_transactions(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """
    Flag expense transactions above a certain amount threshold.
    Excludes credits and payments to focus only on spending.
    
    Args:
        df: Processed transaction DataFrame
        threshold: Amount threshold for flagging
        
    Returns:
        DataFrame with large expense transactions only
    """
    config = load_config()
    threshold = config.get('large_charge_threshold', threshold)
    
    # Filter for expenses only (transaction_type == 'expense')
    expenses_only = df[df['transaction_type'] == 'expense']
    
    # Find large transactions (using absolute value since expenses are negative)
    large_txns = expenses_only[abs(expenses_only['amount']) >= threshold].copy()
    large_txns['flag'] = 'Large Transaction'
    
    # Sort by amount (largest expenses first)
    large_txns = large_txns.sort_values('amount', ascending=True)
    
    return large_txns[['date', 'description', 'amount', 'category', 'flag']]

def save_report(df: pd.DataFrame, name: str, format: str = "csv") -> None:
    """
    Save report DataFrame to file.
    
    Args:
        df: Report DataFrame
        name: Report name (should include card number, e.g., 'card_8592_summary')
        format: Output format (csv or md)
    """
    # Extract card number from report name (e.g., 'card_8592_summary' -> '8592')
    card_number = name.split('_')[1]
    
    # Create card-specific directory
    output_dir = Path("data/processed") / f"card_{card_number}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create report name without card number prefix
    report_name = '_'.join(name.split('_')[2:])  # e.g., 'summary', 'monthly_summary', etc.
    
    if format == "csv":
        df.to_csv(output_dir / f"{report_name}.csv", index=True)
    elif format == "md":
        with open(output_dir / f"{report_name}.md", "w") as f:
            f.write(tabulate(df, headers='keys', tablefmt='pipe', showindex=True))
    
    print(f"Generated {report_name} for card {card_number}")

def calculate_daily_averages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate average daily spending by category for expenses only.
    
    Args:
        df: Processed transaction DataFrame
        
    Returns:
        DataFrame with daily expense averages by category
    """
    # Filter for expenses only
    expenses = df[df['transaction_type'] == 'expense']
    
    # Group by date and category
    daily_totals = expenses.groupby(['date', 'category'])['amount'].sum().abs().reset_index()
    
    # Calculate number of days in the dataset
    date_range = pd.date_range(start=expenses['date'].min(), end=expenses['date'].max())
    num_days = len(date_range)
    
    # Calculate daily averages
    daily_avg = daily_totals.groupby('category')['amount'].sum() / num_days
    
    result = daily_avg.reset_index().rename(columns={'amount': 'daily_average'})
    
    # Sort by daily average spending
    result = result.sort_values('daily_average', ascending=False)
    
    return result

def calculate_weekly_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze expense patterns by day of week.
    
    Args:
        df: Processed transaction DataFrame
        
    Returns:
        DataFrame with average spending by day of week
    """
    # Filter for expenses only
    expenses = df[df['transaction_type'] == 'expense']
    
    # Add day of week column
    expenses['day_of_week'] = pd.to_datetime(expenses['date']).dt.day_name()
    
    # Calculate statistics (use absolute values for expenses)
    weekly_patterns = expenses.groupby('day_of_week').agg({
        'amount': ['count', 'sum', 'mean']
    })
    
    weekly_patterns.columns = ['transaction_count', 'total_spent', 'average_spent']
    weekly_patterns = weekly_patterns.reset_index()
    
    # Take absolute values
    weekly_patterns['total_spent'] = weekly_patterns['total_spent'].abs()
    weekly_patterns['average_spent'] = weekly_patterns['average_spent'].abs()
    
    # Sort by total spent
    weekly_patterns = weekly_patterns.sort_values('total_spent', ascending=False)
    
    return weekly_patterns

def generate_detailed_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a detailed summary of transactions by category, separating spending and payments.
    """
    # Separate expenses and payments
    expenses = df[df['transaction_type'] == 'expense']
    payments = df[df['transaction_type'] == 'payment']
    
    # Calculate spending statistics
    spending_stats = expenses.groupby('category').agg({
        'amount': ['count', 'sum', 'mean', 'min', 'max', 'std']
    }).reset_index()
    
    spending_stats.columns = ['category', 'transaction_count', 'total_spent', 
                            'average_spent', 'min_spent', 'max_spent', 'std_spent']
    
    # Calculate payment statistics
    payment_stats = payments.groupby('category').agg({
        'amount': ['count', 'sum', 'mean', 'min', 'max', 'std']
    }).reset_index()
    
    payment_stats.columns = ['category', 'payment_count', 'total_payments', 
                           'average_payment', 'min_payment', 'max_payment', 'std_payment']
    
    # Calculate percentages
    total_spent = abs(spending_stats['total_spent'].sum())
    spending_stats['percentage_of_spending'] = (abs(spending_stats['total_spent']) / total_spent * 100).round(2)
    
    # Merge spending and payment stats
    summary = pd.merge(spending_stats, payment_stats, on='category', how='outer').fillna(0)
    
    return summary

def generate_card_summary(df: pd.DataFrame, account_number: str) -> pd.DataFrame:
    """
    Generate a standardized summary for a specific account.
    
    Args:
        df: Processed transaction DataFrame
        account_number: Account identifier
        
    Returns:
        DataFrame with standardized account summary
    """
    # Calculate basic statistics
    summary = {
        'account_number': account_number,
        'analysis_period': f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}",
        'total_transactions': len(df),
        'total_amount': df['amount'].sum(),
        'average_transaction': df['amount'].mean(),
        'largest_transaction': df['amount'].max(),
        'smallest_transaction': df['amount'].min(),
        'transaction_std_dev': df['amount'].std()
    }
    
    return pd.DataFrame([summary])

def generate_standardized_reports(df: pd.DataFrame, account_number: str) -> None:
    """
    Generate all standardized reports for a specific account.
    
    Args:
        df: Processed transaction DataFrame
        account_number: Account identifier
    """
    print(f"\nGenerating reports for account {account_number}...")
    
    # Generate account summary
    account_summary = generate_card_summary(df, account_number)
    save_report(account_summary, f"account_{account_number}_summary")
    
    # Generate monthly summary
    monthly_summary = generate_monthly_summary(df)
    save_report(monthly_summary, f"account_{account_number}_monthly_summary")
    
    # Generate top merchants
    top_merchants = identify_top_merchants(df)
    save_report(top_merchants, f"account_{account_number}_top_merchants")
    
    # Generate large transactions
    config = load_config()
    large_txns = flag_large_transactions(df, config.get('large_charge_threshold', 300))
    save_report(large_txns, f"account_{account_number}_large_transactions")
    
    # Generate weekly patterns
    weekly_patterns = calculate_weekly_patterns(df)
    save_report(weekly_patterns, f"account_{account_number}_weekly_patterns")
    
    # Generate detailed summary
    detailed_summary = generate_detailed_summary(df)
    save_report(detailed_summary, f"account_{account_number}_detailed_summary")
    
    print(f"Completed report generation for account {account_number}")

def generate_all_reports() -> None:
    """Generate all financial analysis reports for each account."""
    df = load_processed_data()
    
    if df.empty:
        print("No processed data found. Please run the ingest and categorize steps first.")
        return
    
    # Get unique account numbers
    account_numbers = df['account_number'].unique()
    
    print(f"Processing {len(account_numbers)} accounts...")
    
    for account_number in account_numbers:
        # Filter data for this account
        account_df = df[df['account_number'] == account_number]
        generate_standardized_reports(account_df, account_number)
    
    print(f"\nAnalysis complete. Reports generated in data/processed/ for accounts: {', '.join(account_numbers)}")
    print("Reports are organized in separate directories for each account.")

def cleanup_directories() -> None:
    """Clean up all report directories."""
    processed_dir = Path("data/processed")
    if processed_dir.exists():
        shutil.rmtree(processed_dir)
        processed_dir.mkdir(parents=True, exist_ok=True) 