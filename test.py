import unittest
from pathlib import Path
import pandas as pd
import shutil
import os

from src import ingest, categorize, report

class TestFinancialAnalyzer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test directories and sample data."""
        # Create test directories
        cls.test_dirs = {
            'raw': Path('data/raw'),
            'interim': Path('data/interim'),
            'processed': Path('data/processed')
        }
        
        for dir_path in cls.test_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create sample test data
        cls.sample_data = pd.DataFrame({
            'Transaction Date': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'Posted Date': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'Card No.': ['8592', '8592', '8592'],
            'Description': ['TEST MERCHANT 1', 'TEST MERCHANT 2', 'TEST MERCHANT 3'],
            'Category': ['Test1', 'Test2', 'Test3'],
            'Debit': [100.00, 200.00, 300.00],
            'Credit': [None, None, None]
        })
        
        # Save sample data
        cls.sample_data.to_csv(cls.test_dirs['raw'] / 'test_card_8592.csv', index=False)
    
    def test_ingest(self):
        """Test the ingest module."""
        # Test file listing
        files = ingest.list_raw_files()
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].name.endswith('.csv'))
        
        # Test CSV parsing
        df = ingest.parse_csv(files[0])
        self.assertEqual(len(df), 3)
        self.assertIn('amount', df.columns)
        self.assertIn('date', df.columns)
        self.assertIn('description', df.columns)
    
    def test_categorize(self):
        """Test the categorization module."""
        # First run ingest to get data
        files = ingest.list_raw_files()
        df = ingest.parse_csv(files[0])
        df = ingest.normalize_transactions(df)
        
        # Test categorization
        categorized_df = categorize.categorize_dataframe(df)
        self.assertIn('category', categorized_df.columns)
    
    def test_report(self):
        """Test the reporting module."""
        # First run ingest and categorize
        files = ingest.list_raw_files()
        df = ingest.parse_csv(files[0])
        df = ingest.normalize_transactions(df)
        df = categorize.categorize_dataframe(df)
        
        # Ensure date is datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Test report generation
        summary = report.generate_card_summary(df, '8592')
        self.assertIn('card_number', summary.columns)
        self.assertEqual(summary.iloc[0]['card_number'], '8592')
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test directories."""
        for dir_path in cls.test_dirs.values():
            if dir_path.exists():
                shutil.rmtree(dir_path)

if __name__ == '__main__':
    unittest.main() 