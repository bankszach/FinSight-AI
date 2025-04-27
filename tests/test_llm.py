import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

import pytest
from src.llm import classify
from src.cache import get, put

def test_cache_operations():
    # Test cache put and get
    test_desc = "TEST TRANSACTION"
    test_cat = "Groceries"
    test_vendor = "Test Store"
    
    # Put in cache
    put(test_desc, test_cat, test_vendor)
    
    # Get from cache
    result = get(test_desc)
    assert result == (test_cat, test_vendor)

def test_llm_classification():
    # Test with a simple transaction
    description = "Walmart Grocery Purchase"
    category, vendor = classify(description)
    
    # Verify category is from our list
    valid_categories = ["Groceries", "Dining", "Fuel", "Utilities", "Subscriptions", 
                       "Insurance", "Shopping", "Entertainment", "Medical", 
                       "Transportation", "Services", "Credit Card", "Rent", 
                       "Car Payment", "Income", "Refund"]
    assert category in valid_categories
    
    # Verify vendor is reasonable length
    assert len(vendor) <= 30
    
    # Verify cache was populated
    cached_result = get(description)
    assert cached_result == (category, vendor)

def test_llm_unknown_transaction():
    # Test with a very obscure transaction
    description = "XKCD-1234-5678-9012"
    category, vendor = classify(description)
    
    # Should default to "Services" for unknown transactions
    assert category == "Services"
    assert len(vendor) <= 30 