import unittest
from typing import List, Dict, Any
from src.transformation import DataTransformer

class TestDataTransformer(unittest.TestCase):
    def setUp(self) -> None:
        self.transformer = DataTransformer()

    def test_transform_data(self) -> None:
        raw_List[Dict[str, Any]] = [
            {
                "icao24": "ABC123",
                "callsign": "FLIGHT123",
                "origin_country": "United States",
                "time_position": 1609459200,
                "other_field": "value"
            }
        ]
        
        transformed_data = self.transformer.transform_data(raw_data)
        
        self.assertEqual(len(transformed_data), 1)
        self.assertIn("icao24", transformed_data[0])
        self.assertIn("callsign", transformed_data[0])
        self.assertIn("origin_country", transformed_data[0])
        self.assertIn("enriched_field", transformed_data[0])  # Assuming enrich_data adds this field
        self.assertIsInstance(transformed_data[0]["icao24"], str)
        self.assertIsInstance(transformed_data[0]["callsign"], str)
        self.assertIsInstance(transformed_data[0]["origin_country"], str)

if __name__ == "__main__":
    unittest.main()