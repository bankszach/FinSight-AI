"""
Module for ingesting and normalizing financial statement data.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import PyPDF2
import yaml

def read_config() -> Dict:
    """Read and parse the config.yml file."""
    with open("config.yml", "r") as f:
        return yaml.safe_load(f)

def list_raw_files() -> List[Path]:
    """List all CSV and PDF files in the data/raw directory."""
    raw_dir = Path("data/raw")
    # Get all files that end with .csv (including .csv.csv)
    csv_files = list(raw_dir.glob("*.csv")) + list(raw_dir.glob("*.csv.csv"))
    # Get PDF files
    pdf_files = list(raw_dir.glob("*.pdf"))
    return csv_files + pdf_files

def parse_csv(file_path: Path) -> pd.DataFrame:
    """Parse a CSV file into a standardized DataFrame format."""
    # Read CSV file
    df = pd.read_csv(file_path)
    
    # Extract account number from filename
    # Format examples: quicksilver-8592-jan-apr-2025.csv or usaa-checking-8087.csv
    account_number = file_path.stem.split('-')[1]  # Get '8592' or '8087'
    
    # Normalize column names to lowercase
    df.columns = df.columns.str.lower()
    
    # Handle different date column names
    date_col = 'transaction date' if 'transaction date' in df.columns else 'date'
    df['date'] = pd.to_datetime(df[date_col])
    
    # Handle different amount formats
    if 'credit' in df.columns and 'debit' in df.columns:
        # Capital One format: Credit and Debit columns
        df['amount'] = df['credit'].fillna(0) - df['debit'].fillna(0)
    else:
        # USAA format: Single Amount column
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    
    # Normalize description and category columns
    desc_col = 'description' if 'description' in df.columns else 'original description'
    df['description'] = df[desc_col]
    df['category'] = df['category']
    
    # Add transaction type (positive amounts are payments, negative are expenses)
    df['transaction_type'] = 'expense'
    df.loc[df['amount'] > 0, 'transaction_type'] = 'payment'
    
    # Add account number
    df['account_number'] = account_number
    
    # Select and return standardized columns
    return df[['date', 'description', 'amount', 'category', 'account_number', 'transaction_type']]

def parse_pdf(file_path: Path) -> pd.DataFrame:
    """
    Parse a PDF statement and extract transactions.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        DataFrame with same structure as parse_csv()
    """
    # TODO: Implement PDF parsing and normalization
    pass

def normalize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize transaction data to ensure consistent format and clean data.
    
    Args:
        df: Raw transaction DataFrame
        
    Returns:
        Normalized DataFrame with consistent data types and cleaned values
    """
    # Ensure date is in ISO format
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    # Clean description text
    df['description'] = df['description'].str.strip()
    
    # Ensure amount is numeric and handle any missing values
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    
    # Clean category names
    df['category'] = df['category'].str.strip()
    
    # Ensure card_number is string
    df['account_number'] = df['account_number'].astype(str)
    
    return df

def save_interim_data(df: pd.DataFrame, source_file: Path) -> None:
    """
    Save processed data to interim directory.
    
    Args:
        df: Processed DataFrame
        source_file: Original source file path
    """
    # Create interim directory if it doesn't exist
    interim_dir = Path("data/interim")
    interim_dir.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV with _processed suffix
    output_file = interim_dir / f"{source_file.stem}_processed.csv"
    df.to_csv(output_file, index=False)
    print(f"Saved processed data to {output_file}")

def process_all_files() -> None:
    """
    Process all raw files and save normalized data.
    """
    files = list_raw_files()
    for file_path in files:
        if file_path.suffix.lower() == '.csv':
            df = parse_csv(file_path)
        elif file_path.suffix.lower() == '.pdf':
            df = parse_pdf(file_path)
        else:
            continue
            
        # Normalize the data before saving
        df = normalize_transactions(df)
        save_interim_data(df, file_path)

if __name__ == "__main__":
    process_all_files()
    print("Completed processing all raw files.") 