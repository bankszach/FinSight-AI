import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from datetime import datetime

def load_transactions():
    try:
        df = pd.read_csv('data/processed/account_8087/transactions.csv')
        df['date'] = pd.to_datetime(df['date'])
        df['desc_u'] = df['description'].str.upper()
        return df
    except Exception as e:
        print(f"Error loading transactions: {e}")
        return None

def match_vendor(desc, keywords):
    return any(k in desc for k in keywords)

def analyze_income(df):
    # Define income sources
    INCOME_MAP = {
        'Tower Glass': ['TOWER GLASS'],
        'VA Benefits': ['VETERANS AFFAIRS', 'VA DEPARTMENT'],
        'Education Benefits': ['EDUCATION BENEFITS'],
        'Robert Cromean': ['ROBERT CROMEAN'],
        'Refunds': ['REFUND', 'RETURN', 'CREDIT'],
        'Transfers': ['TRANSFER', 'ZELLE', 'VENMO']
    }
    
    # Filter for positive amounts only
    df_income = df[df['amount'] > 0].copy()
    
    # Categorize income
    income_sources = {}
    for source, keywords in INCOME_MAP.items():
        mask = df_income['desc_u'].apply(lambda x: match_vendor(x, keywords))
        income_sources[source] = df_income[mask]
    
    results = {}
    for source, data in income_sources.items():
        if not data.empty:
            results[source] = {
                'total': data['amount'].sum(),
                'count': len(data),
                'average': data['amount'].mean(),
                'min': data['amount'].min(),
                'max': data['amount'].max()
            }
    return results

def analyze_expenses(df):
    if df is None:
        return {}
        
    # Filter for negative amounts
    df_expenses = df[df['amount'] < 0].copy()
    
    # Define expense categories with vendor mappings
    EXPENSE_MAP = {
        'Rent': ['AMERICAN HERITAG', 'APPFOLIO'],
        'Utilities': ['SDGE', 'GAS & ELECTRIC', 'SMART ENERGY', 'COSD', 'LANDFILL', 'SPECTRUM', 'GOOGLE FI'],
        'Insurance': ['GEICO', 'USAA', 'INSURANCE', 'DENTAL', 'AGI'],
        'Groceries': ['COSTCO', 'VONS', 'TRADER JOE', 'INSTACART', 'IC*', 'RALPHS', 'ALBERTSON', 'SPROUTS', 'WALMART', 'TARGET', 'GROCERY', 'WHSE', 'INSTACART*', 'IC*', 'COSTCO', 'VON\'S', 'COSTCO WHSE', 'MYK CATERING'],
        'Dining': ['DD *', 'DOORDASH', 'UBER EATS', 'GRUBHUB', 'TACO', 'BURRITO', 'SUBWAY', 'STARBUCKS', 'PANDA', 'CAFE', 'BBQ', 'PIZZA', 'GRILL', 'RESTAURANT', 'DD *', 'DOORDASH', 'UBER EATS', 'STARBUCKS', 'COFFEE', '*DOORDASH', 'TACO BELL', 'IT\'S BREAK TIME', 'JUAN VAZQUEZ', 'PARADISE BIRYANI', 'SILVER FOX'],
        'Fuel': ['CHEVRON', 'SHELL', 'ARCO', 'CIRCLE K', '7-ELEVEN', '76', 'GAS', 'FUEL'],
        'Car Payment': ['ZELLE AUSTIN BANKS'],
        'Subscriptions': ['OPENAI', 'CHATGPT', 'VERCEL', 'HOSTINGER', 'NOTION', 'PORKBUN', 'FI ', 'SPECTRUM', 'SPOTIFY', 'YOUTUBE', 'CRUNCHYROLL', 'MIDJOURNEY', 'MINECRAFT', 'INSTACART*SUBSCRIP', 'CHATGPT', 'FI ', 'SPECTRUM', 'VERCEL', 'OPENAI', '*CHATGPT', 'GOOGLE *FI', 'GOOGLE FI', 'PARAMOUNT+', 'RING', 'PLAYSTATION'],
        'Cash Withdrawals': ['ATM'],
        'External Transfers': ['ZELLE', 'VENMO'],
        'Entertainment': ['BREWSKIS', 'LIQUOR LAND', 'GEEKS CANDY', 'DAISO', 'ARCADE', 'REGAL CINEMAS'],
        'Transportation': ['UBER TRIP'],
        'Shopping': ['TIKTOK', 'EXCHANGE', 'SAN DIEGO CA', 'THE HOME DEPOT', 'PACABOL', 'BAYSHORE', 'EXPRESS CONVENIENT', 'NATIONAL CITYCA'],
        'Credit Card Payments': ['CAPITAL ONE', 'COMENITY', 'CREDIT CARD'],
        'Loans': ['ONEMAIN']
    }
    
    # Categorize expenses
    expense_categories = {}
    for category, keywords in EXPENSE_MAP.items():
        mask = df_expenses['desc_u'].apply(lambda x: match_vendor(x, keywords))
        expense_categories[category] = df_expenses[mask]
    
    results = {}
    for category, data in expense_categories.items():
        if not data.empty:
            data_copy = data.copy()
            data_copy['month'] = data_copy['date'].dt.to_period('M')
            monthly_avg = abs(data_copy.groupby('month')['amount'].sum().mean())
            
            results[category] = {
                'total': abs(data['amount'].sum()),
                'count': len(data),
                'average': abs(data['amount'].mean()),
                'monthly_average': monthly_avg,
                'min': data['amount'].min(),
                'max': data['amount'].max(),
                'transactions': data
            }
    
    # Find uncaptured transactions
    captured = pd.concat([expense_categories[cat] for cat in expense_categories if not expense_categories[cat].empty])
    uncaptured = df_expenses.drop(captured.index)
    
    print("\n" + "="*50)
    print("DIAGNOSTIC INFORMATION")
    print("="*50)
    
    print("\nCategory Totals:")
    for cat in ['Groceries', 'Dining', 'Subscriptions']:
        if cat in results:
            total = results[cat]['total']
            count = results[cat]['count']
            print(f"{cat}: ${total:,.2f} ({count} transactions)")
    
    print("\nTop 20 Uncaptured Transactions:")
    if not uncaptured.empty:
        print(uncaptured.nlargest(20, 'amount')[['date', 'description', 'amount']])
    else:
        print("No uncaptured transactions found.")
    
    return results

def analyze_monthly_cash_flow(df):
    df = df.copy()
    df['month'] = df['date'].dt.to_period('M')
    
    # Calculate income and expenses separately
    monthly_income = df[df['amount'] > 0].groupby('month')['amount'].sum()
    monthly_expenses = df[df['amount'] < 0].groupby('month')['amount'].sum()
    monthly_net = monthly_income + monthly_expenses
    
    # Calculate averages
    avg_income = monthly_income.mean()
    avg_expenses = monthly_expenses.mean()
    avg_net = monthly_net.mean()
    
    return {
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'monthly_net': monthly_net,
        'average_income': avg_income,
        'average_expenses': avg_expenses,
        'average_net': avg_net
    }

def plot_monthly_cash_flow(cash_flow):
    months = cash_flow['monthly_net'].index
    income = cash_flow['monthly_income']
    expenses = abs(cash_flow['monthly_expenses'])
    
    plt.figure(figsize=(12, 6))
    plt.bar(months.astype(str), income, label='Income', color='green', alpha=0.6)
    plt.bar(months.astype(str), expenses, label='Expenses', color='red', alpha=0.6)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.2)
    
    plt.title('Monthly Cash Flow')
    plt.xlabel('Month')
    plt.ylabel('Amount ($)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('monthly_cash_flow.png')
    plt.close()

def plot_expense_breakdown(expense_results):
    # Separate essential vs discretionary expenses
    essential = ['Rent', 'Utilities', 'Insurance', 'Car Payment', 'Groceries', 'Fuel']
    discretionary = ['Dining', 'Subscriptions', 'Cash Withdrawals', 'External Transfers']
    
    essential_total = sum(expense_results[cat]['total'] for cat in essential if cat in expense_results)
    discretionary_total = sum(expense_results[cat]['total'] for cat in discretionary if cat in expense_results)
    
    # Create pie chart
    plt.figure(figsize=(10, 8))
    plt.pie([essential_total, discretionary_total], 
            labels=['Essential', 'Discretionary'],
            autopct='%1.1f%%',
            colors=['lightblue', 'lightcoral'])
    plt.title('Essential vs Discretionary Expenses')
    plt.savefig('expense_breakdown.png')
    plt.close()

def main():
    print("Starting analysis...")
    df = load_transactions()
    if df is None:
        print("Failed to load transactions. Exiting.")
        return
    
    print(f"Loaded {len(df)} transactions")
    expense_results = analyze_expenses(df)
    
    if not expense_results:
        print("No expense results found.")
        return
    
    print("\nAnalysis complete.")

if __name__ == "__main__":
    main() 