import pytest
import httpx
from unittest.mock import patch
from analytics.flight_operations_enriched.loader import Loader

@pytest.mark.asyncio
async def test_truncate_insert_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://opensky-network.org/api/states/all',
            method='GET',
            json={'time': 1234567890, 'states': [['icao24_value', 'callsign_value', 'origin_country_value', 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250.0, 180.0, 0.0, 1000, 'squawk_value', False, 'callsign_iata_value', 'airline_name_value', 'airline_iata_value', 'airline_icao_value', 'dep_airport_iata_value', 'arr_airport_iata_value', 'flight_number_value', 'departure_time_value', 'arrival_time_value', 'status_value']]},
        )
        loader = Loader()
        await loader.truncate_insert()

        # Add assertions to verify the data was inserted correctly

@pytest.mark.asyncio
async def test_truncate_insert_null_values():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://opensky-network.org/api/states/all',
            method='GET',
            json={'time': 1234567890, 'states': [['icao24_value', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]},
        )
        loader = Loader()
        await loader.truncate_insert()

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
            await loader.truncate_insert()

@pytest.mark.asyncio
async def test_truncate_insert_empty_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://opensky-network.org/api/states/all',
            method='GET',
            json={'time': 1234567890, 'states': []},
        )
        loader = Loader()
        await loader.truncate_insert()

        # Add assertions to verify how empty responses are handled

@pytest.mark.asyncio
async def test_business_rule_altitude_category():
    row = {'baro_altitude': 2000, 'on_ground': False}
    category = Loader.categorize_altitude(row)
    assert category == 'Low Altitude'

@pytest.mark.asyncio
async def test_business_rule_speed_category():
    row = {'velocity': 250, 'on_ground': False}
    category = Loader.categorize_speed(row)
    assert category == 'Cruise Speed'