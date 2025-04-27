"""
Command-line interface for financial statement analysis.
"""

import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional
import yaml
import shutil

from . import ingest
from . import categorize
from . import report

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Financial Statement Analyzer")
    
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force refresh of all data processing steps"
    )
    
    parser.add_argument(
        "--from",
        dest="start_date",
        type=str,
        help="Start date for analysis (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--to",
        dest="end_date",
        type=str,
        help="End date for analysis (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--output-format",
        choices=["csv", "json", "md"],
        default="csv",
        help="Output format for reports"
    )
    
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clear all data directories after processing"
    )
    
    return parser.parse_args()

def update_config(args) -> None:
    """Update config.yml with command line arguments."""
    with open("config.yml", "r") as f:
        config = yaml.safe_load(f)
    
    if args.start_date:
        config['date_range']['start'] = args.start_date
    if args.end_date:
        config['date_range']['end'] = args.end_date
    
    with open("config.yml", "w") as f:
        yaml.dump(config, f)

def cleanup_directories() -> None:
    """Clear interim and processed directories."""
    directories = [
        "data/interim",
        "data/processed"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            dir_path.mkdir(parents=True, exist_ok=True)
    
    print("Interim and processed directories cleared.")

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Update config if date range specified
    if args.start_date or args.end_date:
        update_config(args)
    
    # Cleanup if requested (do this first to ensure clean state)
    if args.cleanup:
        cleanup_directories()
    
    # Process raw data
    if args.refresh:
        ingest.process_all_files()
        categorize.process_interim_files()
        
        # Check for uncategorized transactions
        uncategorized_files = list(Path("data/processed").glob("**/uncategorized_*.csv"))
        if uncategorized_files:
            print("\n🚨  Unrecognized vendors found!  See the following files:")
            for f in uncategorized_files:
                print(f"  - {f}")
            print("\nPlease review these files and add the missing vendors to config.yml")
    
    # Generate reports
    report.generate_all_reports()
    
    print("Analysis complete. Reports generated in data/processed/")

if __name__ == "__main__":
    main() 