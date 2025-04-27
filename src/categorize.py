"""
Module for categorizing transactions using fuzzy matching.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from fuzzywuzzy import fuzz
import yaml
from datetime import datetime
from . import llm

def load_categories(config_path: str = "config.yml") -> Dict[str, List[str]]:
    """
    Load category mapping from config file.
    
    Args:
        config_path: Path to the config file (default: config.yml)
        
    Returns:
        Dictionary mapping categories to lists of keywords
    """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        return {cat: keywords for cat, keywords in config["categories"].items()}

def fuzzy_match(description: str, keywords: List[str], threshold: int = 60) -> bool:
    """
    Check if description matches any keyword using fuzzy matching.
    
    Args:
        description: Transaction description
        keywords: List of keywords to match against
        threshold: Minimum similarity score (0-100)
        
    Returns:
        True if any keyword matches above threshold
    """
    description = description.upper()
    for keyword in keywords:
        keyword = keyword.upper()
        # Try exact match first
        if keyword in description:
            return True
        # Try partial ratio with lower threshold
        if fuzz.partial_ratio(description, keyword) >= threshold:
            return True
        # Try token set ratio for better partial matching
        if fuzz.token_set_ratio(description, keyword) >= threshold:
            return True
    return False

def categorize_transaction(description: str, categories: Dict[str, List[str]]) -> Tuple[str, str]:
    """
    Categorize a single transaction based on its description.
    
    Args:
        description: Transaction description
        categories: Dictionary of category -> keywords
        
    Returns:
        Tuple of (category name, normalized vendor) or ("uncategorized", description)
    """
    desc = description.upper()
    # exact / keyword pass
    for cat, kw in categories.items():
        if any(k in desc for k in kw):
            return cat, description[:30]
    
    # fuzzy pass
    for category, keywords in categories.items():
        if fuzzy_match(description, keywords):
            return category, description[:30]
            
    # if still unknown → LLM
    category, vendor = llm.classify(description)
    return category.lower(), vendor

def categorize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add category and vendor columns to DataFrame based on transaction descriptions.
    
    Args:
        df: DataFrame with transaction data
        
    Returns:
        DataFrame with added category and vendor columns
    """
    categories = load_categories()
    
    # Initialize category and vendor columns
    df['category'] = 'uncategorized'
    df['vendor'] = df['description'].str[:30]
    
    # First pass: exact matches
    for category, keywords in categories.items():
        mask = df['description'].str.upper().str.contains('|'.join(k.upper() for k in keywords), na=False)
        df.loc[mask, 'category'] = category
        df.loc[mask, 'vendor'] = df.loc[mask, 'description'].str[:30]
    
    # Second pass: fuzzy matches
    for category, keywords in categories.items():
        mask = df['category'] == 'uncategorized'
        if not mask.any():
            continue
        fuzzy_mask = df.loc[mask, 'description'].apply(
            lambda x: any(fuzzy_match(x, [k]) for k in keywords)
        )
        df.loc[mask & fuzzy_mask, 'category'] = category
        df.loc[mask & fuzzy_mask, 'vendor'] = df.loc[mask & fuzzy_mask, 'description'].str[:30]
    
    # Final pass: LLM for remaining uncategorized
    uncategorized_mask = df['category'] == 'uncategorized'
    if uncategorized_mask.any():
        uncategorized_descriptions = df.loc[uncategorized_mask, 'description'].tolist()
        results = llm.batch_classify(uncategorized_descriptions)
        for i, (cat, vendor) in enumerate(results):
            idx = df[uncategorized_mask].index[i]
            df.loc[idx, 'category'] = cat
            df.loc[idx, 'vendor'] = vendor
    
    return df

def get_uncategorized_rows(df: pd.DataFrame, categories: Dict[str, List[str]]) -> pd.DataFrame:
    """
    Identify transactions that weren't categorized by the current rules.
    
    Args:
        df: DataFrame with transaction data
        categories: Dictionary of category keywords
        
    Returns:
        DataFrame containing only uncategorized transactions
    """
    mask = df['description'].apply(lambda x: categorize_transaction(x, categories)) == "uncategorized"
    return df[mask][['date', 'description', 'amount']]

def process_interim_files() -> None:
    """
    Process all files in the interim directory and save categorized versions.
    """
    interim_dir = Path("data/interim")
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    categories = load_categories()
    
    for file_path in interim_dir.glob("*.csv"):
        df = pd.read_csv(file_path)
        df = categorize_dataframe(df)
        
        # Extract account number from filename
        account_number = df['account_number'].iloc[0]
        
        # Create account-specific directory
        account_dir = processed_dir / f"account_{account_number}"
        account_dir.mkdir(parents=True, exist_ok=True)
        
        # Save categorized transactions
        output_file = account_dir / "transactions.csv"
        df.to_csv(output_file, index=False)
        
        # Save uncategorized transactions
        uncategorized = get_uncategorized_rows(df, categories)
        if not uncategorized.empty:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            uncategorized_file = account_dir / f"uncategorized_{timestamp}.csv"
            uncategorized.to_csv(uncategorized_file, index=False)

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