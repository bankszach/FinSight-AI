import pandas as pd
import numpy as np
from pathlib import Path

def analyze_large_transactions(threshold=300):
    # Read consolidated transactions
    df = pd.read_csv("data/processed/account_8087/transactions.csv")
    df['date'] = pd.to_datetime(df['date'])
    
    # Filter for large transactions (absolute value > threshold)
    large_txns = df[abs(df['amount']) > threshold].copy()
    large_txns = large_txns.sort_values('amount')
    
    # Create output directory if it doesn't exist
    Path("data/reports").mkdir(parents=True, exist_ok=True)
    
    # Save large transactions report
    large_txns.to_csv("data/reports/large_transactions.csv", index=False)
    print(f"\nLarge Transactions (>${threshold:,.2f}):")
    print(f"Found {len(large_txns)} transactions")
    print("\nTop 10 largest transactions:")
    print(large_txns.nlargest(10, 'amount')[['date', 'description', 'amount', 'category', 'account']])
    
    return large_txns

def analyze_top_merchants(min_amount=50):
    # Read consolidated transactions
    df = pd.read_csv("data/processed/account_8087/transactions.csv")
    
    # Group by description and calculate metrics
    merchant_summary = df.groupby('description').agg({
        'amount': ['count', 'sum', 'mean'],
        'category': 'first'  # Get the most common category for each merchant
    }).reset_index()
    
    # Flatten column names
    merchant_summary.columns = ['merchant', 'transaction_count', 'total_spend', 'average_spend', 'category']
    
    # Sort by absolute total spend
    merchant_summary['abs_total_spend'] = abs(merchant_summary['total_spend'])
    merchant_summary = merchant_summary.sort_values('abs_total_spend', ascending=False)
    
    # Filter for merchants with significant spend
    significant_merchants = merchant_summary[merchant_summary['abs_total_spend'] > min_amount].copy()
    
    # Save merchant analysis
    significant_merchants.to_csv("data/reports/top_merchants.csv", index=False)
    
    print("\nTop Merchant Analysis:")
    print(f"Analyzed {len(significant_merchants)} merchants with total spend >${min_amount:,.2f}")
    print("\nTop 10 merchants by total spend:")
    print(significant_merchants.head(10)[['merchant', 'transaction_count', 'total_spend', 'average_spend', 'category']])
    
    return significant_merchants

if __name__ == "__main__":
    print("Analyzing high-impact financial levers...")
    large_txns = analyze_large_transactions(threshold=300)
    top_merchants = analyze_top_merchants(min_amount=50) 