import unittest
from unittest.mock import patch, AsyncMock
from src.extraction import DataExtractor

class TestDataExtractor(unittest.TestCase):

    @patch('src.extraction.aiohttp.ClientSession')
    async def test_fetch_opensky_data(self, mock_session: AsyncMock) -> None:
        mock_response = AsyncMock()
        mock_response.json.return_value = {'states': [{'icao24': 'abc123', 'callsign': 'ABC123'}]}
        mock_response.raise_for_status = AsyncMock()
        mock_session.return_value.__aenter__.return_value.get.return_value = mock_response

        extractor = DataExtractor()
        data = await extractor.fetch_opensky_data()

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['icao24'], 'abc123')
        self.assertEqual(data[0]['callsign'], 'ABC123')

    @patch('src.extraction.aiohttp.ClientSession')
    async def test_fetch_adsb_data(self, mock_session: AsyncMock) -> None:
        mock_response = AsyncMock()
        mock_response.json.return_value = {'aircraft': [{'icao24': 'abc123', 'model': 'Boeing 737'}]}
        mock_response.raise_for_status = AsyncMock()
        mock_session.return_value.__aenter__.return_value.get.return_value = mock_response

        extractor = DataExtractor()
        data = await extractor.fetch_adsb_data('abc123')

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['icao24'], 'abc123')
        self.assertEqual(data[0]['model'], 'Boeing 737')

if __name__ == '__main__':
    unittest.main()