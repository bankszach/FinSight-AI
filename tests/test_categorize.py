"""
Tests for the categorize module.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil
import unittest

from src.categorize import (
    load_categories,
    fuzzy_match,
    categorize_transaction,
    categorize_dataframe
)
from src import report, categorize

@pytest.fixture
def sample_transactions():
    """Sample transaction data for testing."""
    return pd.DataFrame({
        "description": [
            "AMAZON.COM",
            "STARBUCKS",
            "WALMART",
            "UBER RIDE",
            "UNKNOWN MERCHANT"
        ],
        "amount": [-50.00, -5.00, -100.00, -25.00, -10.00]
    })

@pytest.fixture
def temp_config():
    """Create temporary config file for testing."""
    config = {
        "categories": {
            "shopping": ["AMAZON", "WALMART"],
            "dining": ["STARBUCKS"],
            "transportation": ["UBER", "LYFT"]
        }
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        import yaml
        yaml.dump(config, f)
        return Path(f.name)

def test_load_categories(temp_config):
    """Test loading categories from config."""
    categories = load_categories(str(temp_config))
    assert isinstance(categories, dict)
    assert "shopping" in categories
    assert "AMAZON" in categories["shopping"]

def test_fuzzy_match():
    """Test fuzzy matching functionality."""
    assert fuzzy_match("AMAZON PRIME", ["AMAZON"]) is True
    assert fuzzy_match("STARBUCKS COFFEE", ["STARBUCKS"]) is True
    assert fuzzy_match("UNKNOWN", ["AMAZON"]) is False

def test_categorize_transaction(temp_config):
    """Test single transaction categorization."""
    categories = load_categories()
    assert categorize_transaction("AMAZON.COM", categories) == "shopping"
    assert categorize_transaction("STARBUCKS", categories) == "dining"
    assert categorize_transaction("UNKNOWN", categories) == "uncategorized"

def test_categorize_dataframe(sample_transactions, temp_config):
    """Test DataFrame categorization."""
    categorized = categorize_dataframe(sample_transactions)
    assert "category" in categorized.columns
    assert categorized.loc[0, "category"] == "shopping"
    assert categorized.loc[1, "category"] == "dining"
    assert categorized.loc[4, "category"] == "uncategorized"

class TestCategorize(unittest.TestCase):
    def test_no_uncategorized(self):
        """Test that all transactions are properly categorized."""
        df = report.load_processed_data()
        if not df.empty:
            uncategorized_count = (df['category'] == 'uncategorized').sum()
            self.assertEqual(uncategorized_count, 0, 
                           f"Found {uncategorized_count} uncategorized transactions")
    
    def test_get_uncategorized_rows(self):
        """Test the uncategorized rows detection function."""
        # Create test data
        test_data = pd.DataFrame({
            'date': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'description': ['KNOWN VENDOR', 'UNKNOWN VENDOR', 'ANOTHER KNOWN'],
            'amount': [-10.00, -20.00, -30.00],
            'category': ['Groceries', 'uncategorized', 'Dining']
        })
        
        # Test categories
        test_categories = {
            'Groceries': ['KNOWN'],
            'Dining': ['ANOTHER']
        }
        
        # Get uncategorized rows
        uncategorized = categorize.get_uncategorized_rows(test_data, test_categories)
        
        # Verify only one row is uncategorized
        self.assertEqual(len(uncategorized), 1)
        self.assertEqual(uncategorized.iloc[0]['description'], 'UNKNOWN VENDOR') 