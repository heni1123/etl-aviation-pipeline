import pytest
import httpx
from unittest.mock import AsyncMock
from loader import Loader  # Assuming the loader class is defined in loader.py

@pytest.fixture
async def mock_httpx_client():
    async with httpx.AsyncClient(transport=httpx.MockTransport()) as client:
        yield client

@pytest.mark.asyncio
async def test_truncate_insert_happy_path(mock_httpx_client):
    loader = Loader(target_db='analytics.cible', http_client=mock_httpx_client)
    mock_httpx_client.add_response(
        method='GET',
        url='https://opensky-network.org/api/states/all',
        json={'states': [['icao24_value', 'callsign_value', 'origin_country_value', 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 1000, 'squawk_value', False, 'callsign_iata_value', 'airline_name_value', 'airline_iata_value', 'airline_icao_value', 'dep_airport_iata_value']]},
    )
    await loader.truncate_insert()

    # Add assertions to verify the data was inserted correctly

@pytest.mark.asyncio
async def test_truncate_insert_with_null_values(mock_httpx_client):
    loader = Loader(target_db='analytics.cible', http_client=mock_httpx_client)
    mock_httpx_client.add_response(
        method='GET',
        url='https://opensky-network.org/api/states/all',
        json={'states': [['icao24_value', None, 'origin_country_value', 1234567890, 1234567890, None, None, None, False, None, None, None, None, None, False, None, None, None, None, None]]},
    )
    await loader.truncate_insert()

    # Add assertions to verify how null values are handled

@pytest.mark.asyncio
async def test_truncate_insert_rate_limit(mock_httpx_client):
    loader = Loader(target_db='analytics.cible', http_client=mock_httpx_client)
    mock_httpx_client.add_response(
        method='GET',
        url='https://opensky-network.org/api/states/all',
        status_code=429,
        json={'error': 'Rate limit exceeded'},
    )
    with pytest.raises(httpx.HTTPStatusError):
        await loader.truncate_insert()

@pytest.mark.asyncio
async def test_truncate_insert_empty_response(mock_httpx_client):
    loader = Loader(target_db='analytics.cible', http_client=mock_httpx_client)
    mock_httpx_client.add_response(
        method='GET',
        url='https://opensky-network.org/api/states/all',
        json={'states': []},
    )
    await loader.truncate_insert()

    # Add assertions to verify how empty responses are handled

@pytest.mark.asyncio
async def test_business_rule_1(mock_httpx_client):
    loader = Loader(target_db='analytics.cible', http_client=mock_httpx_client)
    mock_httpx_client.add_response(
        method='GET',
        url='https://opensky-network.org/api/states/all',
        json={'states': [['icao24_value', 'callsign_value', 'origin_country_value', 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 1000, 'squawk_value', False, 'callsign_iata_value', 'airline_name_value', 'airline_iata_value', 'airline_icao_value', 'dep_airport_iata_value']]},
    )
    result = await loader.apply_business_rule_1({'icao24': 'icao24_value'})
    assert result['icao24'] == 'icao24_value'

@pytest.mark.asyncio
async def test_business_rule_2(mock_httpx_client):
    loader = Loader(target_db='analytics.cible', http_client=mock_httpx_client)
    mock_httpx_client.add_response(
        method='GET',
        url='https://opensky-network.org/api/states/all',
        json={'states': [['icao24_value', 'callsign_value', 'origin_country_value', 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 1000, 'squawk_value', False, 'callsign_iata_value', 'airline_name_value', 'airline_iata_value', 'airline_icao_value', 'dep_airport_iata_value']]},
    )
    result = await loader.apply_business_rule_2({'callsign': ' callsign_value '})
    assert result['callsign'] == 'CALLSIGN_VALUE'

# Additional tests for other business rules can be added similarly.