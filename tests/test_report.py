"""
Tests for the report module.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from src.report import (
    generate_monthly_summary,
    calculate_rolling_averages,
    identify_top_merchants,
    flag_large_transactions
)

@pytest.fixture
def sample_categorized_data():
    """Sample categorized transaction data for testing."""
    return pd.DataFrame({
        "date": pd.date_range(start="2023-01-01", periods=10, freq="D"),
        "description": [
            "AMAZON.COM",
            "STARBUCKS",
            "WALMART",
            "UBER RIDE",
            "AMAZON.COM",
            "STARBUCKS",
            "WALMART",
            "UBER RIDE",
            "AMAZON.COM",
            "LARGE PURCHASE"
        ],
        "amount": [-50.00, -5.00, -100.00, -25.00, -50.00, -5.00, -100.00, -25.00, -50.00, -1000.00],
        "category": [
            "shopping",
            "dining",
            "shopping",
            "transportation",
            "shopping",
            "dining",
            "shopping",
            "transportation",
            "shopping",
            "shopping"
        ]
    })

def test_generate_monthly_summary(sample_categorized_data):
    """Test monthly summary generation."""
    summary = generate_monthly_summary(sample_categorized_data)
    assert isinstance(summary, pd.DataFrame)
    assert "shopping" in summary.columns
    assert "dining" in summary.columns
    assert "transportation" in summary.columns
    assert len(summary) == 1  # All transactions in January

def test_calculate_rolling_averages(sample_categorized_data):
    """Test rolling average calculation."""
    averages = calculate_rolling_averages(sample_categorized_data, months=1)
    assert isinstance(averages, pd.DataFrame)
    assert "shopping" in averages.columns
    assert "dining" in averages.columns
    assert "transportation" in averages.columns

def test_identify_top_merchants(sample_categorized_data):
    """Test top merchant identification."""
    top_merchants = identify_top_merchants(sample_categorized_data, n=3)
    assert isinstance(top_merchants, pd.DataFrame)
    assert len(top_merchants) == 3
    assert "AMAZON.COM" in top_merchants["description"].values
    assert "WALMART" in top_merchants["description"].values
    assert "STARBUCKS" in top_merchants["description"].values

def test_flag_large_transactions(sample_categorized_data):
    """Test large transaction flagging."""
    large_transactions = flag_large_transactions(sample_categorized_data, threshold=500.00)
    assert isinstance(large_transactions, pd.DataFrame)
    assert len(large_transactions) == 1
    assert large_transactions.iloc[0]["description"] == "LARGE PURCHASE"
    assert large_transactions.iloc[0]["amount"] == -1000.00 