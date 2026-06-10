import pytest
from unittest.mock import patch, AsyncMock
from src.loading import DataLoader

class TestDataLoader:
    @pytest.fixture
    def data_loader(self):
        db_url = "postgresql://user:password@localhost:5432/test_db"
        return DataLoader(db_url)

    @patch('src.loading.create_engine')
    async def test_load_data(self, mock_create_engine, data_loader):
        mock_connection = AsyncMock()
        mock_create_engine.return_value.connect.return_value.__enter__.return_value = mock_connection

        transformed_list = [
            {
                "icao24": "abcd",
                "callsign": "CALLSIGN1",
                "origin_country": "CountryA",
                "destination_country": "CountryB",
                "departure": "2023-10-01T12:00:00Z",
                "arrival": "2023-10-01T14:00:00Z",
                "route": "RouteA",
                "airline": "AirlineA"
            }
        ]

        await data_loader.load_data(transformed_list)

        assert mock_connection.execute.call_count == 1
        mock_connection.execute.assert_called_with(
            "INSERT INTO flight_traffic (icao24, callsign, origin_country, destination_country, "
            "departure, arrival, route, airline) "
            "VALUES (:icao24, :callsign, :origin_country, :destination_country, "
            ":departure, :arrival, :route, :airline)",
            {
                'icao24': 'abcd',
                'callsign': 'CALLSIGN1',
                'origin_country': 'CountryA',
                'destination_country': 'CountryB',
                'departure': '2023-10-01T12:00:00Z',
                'arrival': '2023-10-01T14:00:00Z',
                'route': 'RouteA',
                'airline': 'AirlineA'
            }
        )

    @patch('src.loading.create_engine')
    async def test_load_data_error(self, mock_create_engine, data_loader):
        mock_create_engine.return_value.connect.side_effect = SQLAlchemyError("Database error")

        transformed_list = [
            {
                "icao24": "abcd",
                "callsign": "CALLSIGN1",
                "origin_country": "CountryA",
                "destination_country": "CountryB",
                "departure": "2023-10-01T12:00:00Z",
                "arrival": "2023-10-01T14:00:00Z",
                "route": "RouteA",
                "airline": "AirlineA"
            }
        ]

        with pytest.raises(SQLAlchemyError):
            await data_loader.load_data(transformed_list)