import pytest
import httpx
from unittest.mock import AsyncMock
from generated.e4aa07d8-812f-4dc0-8f4d-131e11434352.loader import Loader

@pytest.fixture
async def mock_httpx():
    async with httpx.AsyncClient(transport=httpx.MockTransport()) as client:
        yield client

@pytest.mark.asyncio
async def test_br1_unique_identifier(mock_httpx):
    mock_httpx.add_response(
        url='https://opensky-network.org/api/states/all',
        method='GET',
        json={'time': 1234567890, 'states': [['icao24_value', 'callsign_value', 'origin_country_value', 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 2000, 'squawk_value', False, 'callsign_iata_value', 'airline_name_value', 'airline_iata_value', 'airline_icao_value', 'dep_airport_iata_value', 'arr_airport_iata_value', 'flight_number_value']]},
    )
    loader = Loader()
    result = await loader.load_data(mock_httpx)
    assert result['icao24'] == 'icao24_value'

@pytest.mark.asyncio
async def test_br2_callsign(mock_httpx):
    mock_httpx.add_response(
        url='https://opensky-network.org/api/states/all',
        method='GET',
        json={'time': 1234567890, 'states': [['icao24_value', 'callsign_value', 'origin_country_value', 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 2000, 'squawk_value', False, 'callsign_iata_value', 'airline_name_value', 'airline_iata_value', 'airline_icao_value', 'dep_airport_iata_value', 'arr_airport_iata_value', 'flight_number_value']]},
    )
    loader = Loader()
    result = await loader.load_data(mock_httpx)
    assert result['callsign'] == 'callsign_value'

@pytest.mark.asyncio
async def test_br3_origin_country(mock_httpx):
    mock_httpx.add_response(
        url='https://opensky-network.org/api/states/all',
        method='GET',
        json={'time': 1234567890, 'states': [['icao24_value', 'callsign_value', 'origin_country_value', 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 2000, 'squawk_value', False, 'callsign_iata_value', 'airline_name_value', 'airline_iata_value', 'airline_icao_value', 'dep_airport_iata_value', 'arr_airport_iata_value', 'flight_number_value']]},
    )
    loader = Loader()
    result = await loader.load_data(mock_httpx)
    assert result['origin_country'] == 'origin_country_value'

@pytest.mark.asyncio
async def test_br4_time_position(mock_httpx):
    mock_httpx.add_response(
        url='https://opensky-network.org/api/states/all',
        method='GET',
        json={'time': 1234567890, 'states': [['icao24_value', 'callsign_value', 'origin_country_value', 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 2000, 'squawk_value', False, 'callsign_iata_value', 'airline_name_value', 'airline_iata_value', 'airline_icao_value', 'dep_airport_iata_value', 'arr_airport_iata_value', 'flight_number_value']]},
    )
    loader = Loader()
    result = await loader.load_data(mock_httpx)
    assert result['time_position'] == 1234567890

@pytest.mark.asyncio
async def test_br5_on_ground(mock_httpx):
    mock_httpx.add_response(
        url='https://opensky-network.org/api/states/all',
        method='GET',
        json={'time': 1234567890, 'states': [['icao24_value', 'callsign_value', 'origin_country_value', 1234567890, 1234567890, 10.0, 10.0, 1000, True, 250, 180, 0, 2000, 'squawk_value', False, 'callsign_iata_value', 'airline_name_value', 'airline_iata_value', 'airline_icao_value', 'dep_airport_iata_value', 'arr_airport_iata_value', 'flight_number_value']]},
    )
    loader = Loader()
    result = await loader.load_data(mock_httpx)
    assert result['on_ground'] is True

@pytest.mark.asyncio
async def test_empty_response(mock_httpx):
    mock_httpx.add_response(
        url='https://opensky-network.org/api/states/all',
        method='GET',
        json={'time': 1234567890, 'states': []},
    )
    loader = Loader()
    result = await loader.load_data(mock_httpx)
    assert result['states'] == []

@pytest.mark.asyncio
async def test_rate_limit(mock_httpx):
    mock_httpx.add_response(
        url='https://opensky-network.org/api/states/all',
        method='GET',
        status_code=429,
        json={'error': 'Rate limit exceeded'},
    )
    loader = Loader()
    with pytest.raises(httpx.HTTPStatusError):
        await loader.load_data(mock_httpx)