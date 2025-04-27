# API Reference

## Overview

This document provides detailed information about the API interfaces and integration points in the Personal Finance Analyzer.

## Core Modules

### 1. Data Ingestion (`ingest.py`)

#### Functions
```python
def read_financial_statement(file_path: str) -> pd.DataFrame:
    """
    Read and parse financial statements from CSV or PDF files.
    
    Args:
        file_path: Path to the financial statement file
        
    Returns:
        DataFrame containing parsed transaction data
    """

def normalize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize transaction data to standard format.
    
    Args:
        df: Raw transaction DataFrame
        
    Returns:
        Normalized DataFrame with standardized columns
    """
```

### 2. Transaction Processing (`categorize.py`)

#### Functions
```python
def categorize_transaction(transaction: dict, rules: dict) -> str:
    """
    Categorize a single transaction using rules and LLM.
    
    Args:
        transaction: Transaction data dictionary
        rules: Categorization rules dictionary
        
    Returns:
        Assigned category string
    """

def process_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process and categorize all transactions in a DataFrame.
    
    Args:
        df: Transaction DataFrame
        
    Returns:
        DataFrame with added category column
    """
```

### 3. LLM Integration (`llm.py`)

#### Classes
```python
class LLMClient:
    """
    Client for interacting with LLM APIs.
    """
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize LLM client.
        
        Args:
            api_key: OpenAI API key
            model: Model to use for processing
        """
    
    def categorize(self, transaction: dict) -> str:
        """
        Categorize transaction using LLM.
        
        Args:
            transaction: Transaction data dictionary
            
        Returns:
            Assigned category string
        """
```

### 4. Analysis Engine (`report.py`)

#### Functions
```python
def generate_monthly_report(df: pd.DataFrame) -> dict:
    """
    Generate monthly financial analysis report.
    
    Args:
        df: Categorized transaction DataFrame
        
    Returns:
        Dictionary containing analysis results
    """

def analyze_spending_patterns(df: pd.DataFrame) -> dict:
    """
    Analyze spending patterns and trends.
    
    Args:
        df: Transaction DataFrame
        
    Returns:
        Dictionary containing pattern analysis
    """
```

## Data Structures

### 1. Transaction Format
```python
{
    'date': 'YYYY-MM-DD',
    'description': str,
    'amount': float,
    'category': str,
    'account': str
}
```

### 2. Analysis Results
```python
{
    'monthly_totals': {
        'income': float,
        'expenses': float,
        'net': float
    },
    'category_breakdown': {
        'category_name': {
            'total': float,
            'count': int,
            'average': float
        }
    },
    'patterns': {
        'trends': list,
        'anomalies': list
    }
}
```

## Configuration

### 1. Environment Variables
```python
OPENAI_API_KEY: str
OPENAI_API_BASE: str
OPENAI_MODEL: str
OPENAI_TEMP: float
```

### 2. Configuration File (`config.yml`)
```yaml
date_range:
  start: 'YYYY-MM-DD'
  end: 'YYYY-MM-DD'

categories:
  category_name:
    - pattern1
    - pattern2

large_charge_threshold: float
currency: str
```

## Error Handling

### 1. Exceptions
```python
class FinancialDataError(Exception):
    """Base exception for financial data processing errors."""

class LLMError(Exception):
    """Exception for LLM API errors."""

class AnalysisError(Exception):
    """Exception for analysis processing errors."""
```

### 2. Error Codes
```python
ERROR_CODES = {
    'INVALID_FORMAT': 100,
    'MISSING_DATA': 101,
    'API_ERROR': 200,
    'PROCESSING_ERROR': 300
}
```

## Integration Examples

### 1. Basic Usage
```python
from src.ingest import read_financial_statement
from src.categorize import process_transactions
from src.report import generate_monthly_report

# Read and process data
df = read_financial_statement('data/raw/statement.csv')
df = process_transactions(df)
report = generate_monthly_report(df)
```

### 2. Custom Categorization
```python
from src.llm import LLMClient
from src.categorize import categorize_transaction

# Initialize LLM client
llm = LLMClient(api_key='your-api-key')

# Categorize transaction
category = categorize_transaction(transaction, rules)
```

### 3. Advanced Analysis
```python
from src.report import analyze_spending_patterns

# Analyze patterns
patterns = analyze_spending_patterns(df)
```

## Performance Considerations

### 1. Batch Processing
```python
# Process transactions in batches
batch_size = 100
for i in range(0, len(df), batch_size):
    batch = df[i:i+batch_size]
    process_transactions(batch)
```

### 2. Caching
```python
# Cache LLM responses
@cache
def categorize_with_llm(transaction):
    return llm.categorize(transaction)
```

### 3. Parallel Processing
```python
# Process transactions in parallel
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor() as executor:
    results = executor.map(process_transaction, transactions)
```

## Security

### 1. API Key Management
```python
# Secure API key handling
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
```

### 2. Data Protection
```python
# Encrypt sensitive data
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher_suite = Fernet(key)
encrypted_data = cipher_suite.encrypt(data)
```

## Monitoring

### 1. Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info('Processing transaction: %s', transaction_id)
```

### 2. Metrics
```python
# Track processing metrics
from prometheus_client import Counter, Histogram

processed_transactions = Counter('processed_transactions_total', 'Total processed transactions')
processing_time = Histogram('processing_time_seconds', 'Time spent processing')
``` 