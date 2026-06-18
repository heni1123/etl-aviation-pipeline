import pytest
import httpx
from unittest.mock import patch
from loader import Loader  # Assuming the Loader class is defined in loader.py

@pytest.mark.asyncio
async def test_truncate_insert_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://opensky-network.org/api/states/all',
            method='GET',
            json={'time': 1234567890, 'states': [['icao24_example', 'callsign_example', 'origin_country_example', 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 5000, 'squawk_example', False, 'callsign_iata_example', 'airline_name_example', 'airline_iata_example', 'airline_icao_example', 'dep_airport_iata_example', 'arr_airport_iata_example', 'flight_number_example', 'departure_time_example', 'arrival_time_example']]},
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
            json={'time': 1234567890, 'states': [['icao24_example', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]},
        )
        loader = Loader()
        await loader.load_data()
        # Add assertions to verify handling of null values

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
            json={'time': 1234567890, 'states': []},
        )
        loader = Loader()
        await loader.load_data()
        # Add assertions to verify handling of empty response

@pytest.mark.asyncio
async def test_business_rule_altitude_category():
    row = {'baro_altitude': 2500, 'on_ground': False}
    category = Loader.categorize_altitude(row)
    assert category == 'Low Altitude'

@pytest.mark.asyncio
async def test_business_rule_speed_category():
    row = {'velocity': 300, 'on_ground': False}
    category = Loader.categorize_speed(row)
    assert category == 'Cruise Speed'