import unittest
import os
import json
from datetime import datetime
from data_fetcher import DataFetcher
from date_checker import DateChecker

class TestHolidayEmail(unittest.TestCase):
    def setUp(self):
        # Create test data directory
        self.test_data_dir = "test_data"
        if not os.path.exists(self.test_data_dir):
            os.makedirs(self.test_data_dir)
        
        # Initialize DataFetcher with test directory
        self.data_fetcher = DataFetcher(self.test_data_dir)
    
    def tearDown(self):
        # Clean up test files
        for file in os.listdir(self.test_data_dir):
            os.remove(os.path.join(self.test_data_dir, file))
        os.rmdir(self.test_data_dir)
    
    def test_fetch_jieqi(self):
        """Test fetching solar terms data."""
        # Use a specific year for testing
        year = 2023
        
        # Fetch data
        data = self.data_fetcher.fetch_jieqi(year)
        
        # Check if data is fetched and saved
        self.assertIsNotNone(data)
        self.assertTrue(os.path.exists(os.path.join(self.test_data_dir, f"jieqi_{year}.json")))
        
        # Check data structure
        self.assertIn("data", data)
        self.assertTrue(len(data["data"]) > 0)
        
        # Check a sample entry
        sample_entry = data["data"][0]
        self.assertIn("name", sample_entry)
        self.assertIn("date", sample_entry)
    
    def test_fetch_holidays(self):
        """Test fetching holiday data."""
        # Use a specific year for testing
        year = 2023
        
        # Fetch data
        data = self.data_fetcher.fetch_holidays(year)
        
        # Check if data is fetched and saved
        self.assertIsNotNone(data)
        self.assertTrue(os.path.exists(os.path.join(self.test_data_dir, f"holiday_{year}.json")))
        
        # Check data structure
        self.assertIn("data", data)
        self.assertTrue(len(data["data"]) > 0)
        
        # Check a sample entry
        sample_entry = data["data"][0]
        self.assertIn("name", sample_entry)
        self.assertIn("dates", sample_entry)
    
    def test_date_checker(self):
        """Test DateChecker functionality."""
        # Create a DateChecker with our test DataFetcher
        date_checker = DateChecker(self.data_fetcher)
        
        # Test getting upcoming special dates
        upcoming = date_checker.get_upcoming_special_dates(days=30)
        
        # There should be some special dates in the next 30 days
        self.assertTrue(len(upcoming) > 0)
        
        # Check the structure of the returned data
        for date_str, type_str, info in upcoming:
            self.assertIn(type_str, ["holiday", "jieqi"])
            self.assertIn("name", info)
            
            # Verify the date format
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                self.fail(f"Date string {date_str} is not in the correct format")

if __name__ == "__main__":
    unittest.main()
