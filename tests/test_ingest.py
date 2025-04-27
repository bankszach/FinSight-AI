"""
Tests for the ingest module.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil

from src.ingest import (
    parse_csv,
    normalize_transactions,
    save_interim_data
)

@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    return """Date,Description,Amount
2023-01-01,AMAZON.COM,50.00
2023-01-02,STARBUCKS,-5.00
2023-01-03,WALMART,-100.00
"""

@pytest.fixture
def sample_csv_file(sample_csv_data):
    """Create a temporary CSV file with sample data."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(sample_csv_data)
        return Path(f.name)

@pytest.fixture
def temp_data_dir():
    """Create temporary data directory structure."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "raw").mkdir()
        (temp_path / "interim").mkdir()
        (temp_path / "processed").mkdir()
        yield temp_path
        shutil.rmtree(temp_dir)

def test_parse_csv(sample_csv_file):
    """Test CSV parsing."""
    df = parse_csv(sample_csv_file)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert list(df.columns) == ["date", "description", "amount"]
    assert df["amount"].dtype == float

def test_normalize_transactions(sample_csv_file):
    """Test transaction normalization."""
    df = parse_csv(sample_csv_file)
    normalized = normalize_transactions(df)
    assert isinstance(normalized, pd.DataFrame)
    assert "date" in normalized.columns
    assert normalized["date"].dtype == "datetime64[ns]"
    assert normalized["amount"].dtype == float

def test_save_interim_data(sample_csv_file, temp_data_dir):
    """Test saving interim data."""
    df = parse_csv(sample_csv_file)
    normalized = normalize_transactions(df)
    save_interim_data(normalized, sample_csv_file)
    
    interim_files = list((temp_data_dir / "interim").glob("*.csv"))
    assert len(interim_files) == 1
    saved_df = pd.read_csv(interim_files[0])
    assert len(saved_df) == len(normalized) 