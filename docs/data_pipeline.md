# Data Pipeline Documentation

## Overview

This document details the data processing pipeline in the Personal Finance Analyzer, from raw data ingestion to final analysis outputs.

## Pipeline Architecture

```
Raw Data → Ingestion → Consolidation → Categorization → Analysis → Insights
(CSV/PDF)  (ingest.py) (consolidate.py) (categorize.py) (report.py)  (LLM)
```

## Component Details

### 1. Data Ingestion (`ingest.py`)

#### Input Sources
- CSV financial statements from multiple accounts
- PDF statements (basic support)
- JSON configuration

#### Processing Steps
1. **File Reading**
   ```python
   def parse_csv(file_path: Path) -> pd.DataFrame:
       # Read CSV file
       df = pd.read_csv(file_path)
       
       # Extract account number from filename
       account_number = file_path.stem.split('-')[1]
       
       # Normalize column names
       df.columns = df.columns.str.lower()
       
       # Handle different date formats
       date_col = 'transaction date' if 'transaction date' in df.columns else 'date'
       df['date'] = pd.to_datetime(df[date_col])
       
       # Handle different amount formats
       if 'credit' in df.columns and 'debit' in df.columns:
           df['amount'] = df['credit'].fillna(0) - df['debit'].fillna(0)
       else:
           df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
   ```

2. **Data Normalization**
   - Date standardization to ISO format
   - Amount formatting and type conversion
   - Description cleaning and standardization
   - Account number extraction from filenames
   - Transaction type classification (expense/payment)

3. **Output**
   - Saves processed files to `data/interim/` with `_processed.csv` suffix
   - Maintains original account information
   - Standardizes column names and data types

### 2. Data Consolidation (`consolidate.py`)

#### Processing Steps
1. **File Collection**
   - Gathers all processed files from `data/interim/`
   - Extracts account information from filenames

2. **Data Merging**
   ```python
   def consolidate_transactions():
       # Read all interim CSV files
       dfs = []
       for file in os.listdir(interim_dir):
           if file.endswith("_processed.csv"):
               df = pd.read_csv(os.path.join(interim_dir, file))
               account_info = file.split("-")[0:2]
               df['account'] = f"{account_info[0]}-{account_info[1]}"
               dfs.append(df)
   ```

3. **Output**
   - Creates a single consolidated file at `data/processed/account_8087/transactions.csv`
   - Maintains account information in the data
   - Sorts transactions by date

### 3. Transaction Processing (`categorize.py`)

#### Categorization Flow
1. **Rule-based Matching**
   - Loads categories from config file
   - Applies exact matches first
   - Uses fuzzy matching for similar descriptions

2. **LLM Fallback**
   - Processes remaining uncategorized transactions
   - Provides category and vendor information
   - Updates the consolidated dataset

### 4. Analysis Engine (`report.py`)

#### Analysis Types
1. **Financial Metrics**
   - Category totals
   - Transaction counts
   - Uncategorized transactions

2. **Diagnostic Information**
   - Top uncaptured transactions
   - Category distribution
   - Transaction patterns

## Data Storage

### Directory Structure
```
data/
├── raw/                     # Original statements
│   ├── account1.csv
│   ├── account2.pdf
│   └── ...
├── interim/                 # Processed data
│   ├── account1_processed.csv
│   ├── account2_processed.csv
│   └── ...
├── processed/               # Consolidated data
│   └── account_8087/
│       └── transactions.csv
└── reports/                 # Analysis outputs
    └── spending_analysis.csv
```

### File Formats
1. **Input**
   - CSV: Bank statements with varying formats
   - PDF: Bank statements (future support)

2. **Intermediate**
   - CSV: Normalized transactions with account info
   - YAML: Category configuration

3. **Output**
   - CSV: Consolidated transactions
   - CSV: Analysis reports

## Data Flow

### 1. Ingestion Phase
```
Raw Files → Parse CSV → Normalize → Save Interim
   (CSV)     (ingest)    (format)    (CSV)
```

### 2. Consolidation Phase
```
Interim Files → Merge → Sort → Save Consolidated
   (CSV)       (consolidate)  (date)    (CSV)
```

### 3. Processing Phase
```
Consolidated → Categorize → Analyze → Report
   (CSV)        (rules/LLM)  (metrics)  (CSV)
```

## Error Handling

### 1. Validation Errors
- Missing required columns
- Invalid date formats
- Non-numeric amounts

### 2. Processing Errors
- File read/write failures
- Category matching failures
- LLM processing errors

### 3. Output Errors
- Directory creation failures
- File write permissions
- Data format issues

## Performance Optimization

### 1. Processing
- Batch processing of transactions
- Efficient data type handling
- Memory-optimized operations

### 2. Storage
- Structured directory organization
- Clear file naming conventions
- Account-specific data storage

### 3. Analysis
- Efficient DataFrame operations
- Categorized data access
- Pattern recognition

## Monitoring

### 1. Metrics
- Transaction counts
- Processing time
- Category distribution
- Uncategorized transactions

### 2. Logging
- Processing steps
- File operations
- Error details
- Category assignments

### 3. Alerts
- Processing failures
- Uncategorized transactions
- Data quality issues

## Security

### 1. Data Protection
- Local file storage
- Account information handling
- Transaction data security

### 2. Privacy
- Account number masking
- Transaction data handling
- Report generation

### 3. Compliance
- Data retention
- Access control
- Audit logging 