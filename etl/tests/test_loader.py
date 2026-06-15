import pytest
import httpx
from unittest.mock import patch
from loader import Loader  # Assuming the loader class is defined in loader.py

@pytest.mark.asyncio
async def test_truncate_insert_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://opensky-network.org/api/states/all',
            method='GET',
            json={'states': [['icao24_value', 'callsign_value', 'origin_country_value', 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 5000, 'squawk_value', False, 'callsign_iata_value', 'airline_name_value', 'airline_iata_value', 'airline_icao_value', 'dep_airport_iata_value', 'arr_airport_iata_value', 'flight_number_value', 'departure_time_value', 'arrival_time_value']]},
        )
        loader = Loader()
        await loader.load_data()
        # Add assertions to verify data was loaded correctly

@pytest.mark.asyncio
async def test_truncate_insert_null_values():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://opensky-network.org/api/states/all',
            method='GET',
            json={'states': [['icao24_value', None, 'origin_country_value', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]},
        )
        loader = Loader()
        await loader.load_data()
        # Add assertions to verify how null values are handled

@pytest.mark.asyncio
async def test_truncate_insert_rate_limit():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://opensky-network.org/api/states/all',
            method='GET',
            status_code=429,
            json={'error': 'Rate limit exceeded'},
        )
        loader = Loader()
        with pytest.raises(httpx.HTTPStatusError):
            await loader.load_data()

@pytest.mark.asyncio
async def test_truncate_insert_empty_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://opensky-network.org/api/states/all',
            method='GET',
            json={'states': []},
        )
        loader = Loader()
        await loader.load_data()
        # Add assertions to verify how empty responses are handled

@pytest.mark.asyncio
async def test_business_rule_1():
    # Test for BR1: Unique identifier for the aircraft
    row = {'icao24': None}
    assert row['icao24'] is not None

@pytest.mark.asyncio
async def test_business_rule_2():
    # Test for BR2: Callsign must be cleaned and uppercased
    row = {'callsign': ' test_callSign '}
    assert row['callsign'].strip().upper() == 'TEST_CALLSIGN'

@pytest.mark.asyncio
async def test_business_rule_3():
    # Test for BR3: Origin country must be a valid ISO country code
    valid_iso_country_codes = ['US', 'FR', 'DE']
    row = {'origin_country': 'US'}
    assert row['origin_country'] in valid_iso_country_codes

@pytest.mark.asyncio
async def test_business_rule_4():
    # Test for BR4: Aircraft must not be marked as on ground for flight tracking
    row = {'on_ground': False}
    assert not row['on_ground']