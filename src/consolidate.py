import pandas as pd
import os
from pathlib import Path

def consolidate_transactions():
    # Create necessary directories
    Path("data/processed/account_8087").mkdir(parents=True, exist_ok=True)
    
    # Read all interim CSV files
    interim_dir = "data/interim"
    dfs = []
    
    for file in os.listdir(interim_dir):
        if file.endswith("_processed.csv"):
            df = pd.read_csv(os.path.join(interim_dir, file))
            # Extract account info from filename
            account_info = file.split("-")[0:2]  # Gets bank name and last 4 digits
            df['account'] = f"{account_info[0]}-{account_info[1]}"
            dfs.append(df)
    
    # Combine all dataframes
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Ensure required columns exist
        required_cols = ['date', 'description', 'amount', 'category', 'account']
        for col in required_cols:
            if col not in combined_df.columns:
                print(f"Warning: Missing required column {col}")
                return False
        
        # Sort by date
        combined_df['date'] = pd.to_datetime(combined_df['date'])
        combined_df = combined_df.sort_values('date')
        
        # Save to processed directory
        output_path = "data/processed/account_8087/transactions.csv"
        combined_df.to_csv(output_path, index=False)
        print(f"Successfully consolidated {len(dfs)} files into {output_path}")
        print(f"Total transactions: {len(combined_df)}")
        return True
    else:
        print("No interim CSV files found to consolidate")
        return False

if __name__ == "__main__":
    consolidate_transactions() 