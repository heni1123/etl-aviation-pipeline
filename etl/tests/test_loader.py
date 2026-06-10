import pytest
import httpx
from unittest.mock import patch
from your_etl_module import Loader  # Adjust the import based on your actual module structure

@pytest.mark.asyncio
async def test_loader_truncate_insert_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://opensky-network.org/api/states/all',
            method='GET',
            json={'time': 1234567890, 'states': [['icao24_value', 'callsign_value', 'origin_country_value', 1234567890, 1234567890, 10.0, 10.0, 1000, False, 200, 180, 0, 1000, 'squawk_value', False, 'callsign_iata_value', 'airline_name_value', 'airline_iata_value', 'airline_icao_value', 'dep_airport_iata_value', 'arr_airport_iata_value', 'flight_number_value', 'other_fields_value']]},
        )
        loader = Loader()
        await loader.truncate_insert()

        # Add assertions to verify the data was inserted correctly
        # Example: assert await loader.get_data_count() == expected_count

@pytest.mark.asyncio
async def test_loader_truncate_insert_null_values():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://opensky-network.org/api/states/all',
            method='GET',
            json={'time': 1234567890, 'states': [['icao24_value', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]},
        )
        loader = Loader()
        await loader.truncate_insert()

        # Add assertions to verify how null values are handled
        # Example: assert await loader.get_data_count() == expected_count

@pytest.mark.asyncio
async def test_loader_truncate_insert_rate_limit():
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
async def test_loader_truncate_insert_empty_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://opensky-network.org/api/states/all',
            method='GET',
            json={'time': 1234567890, 'states': []},
        )
        loader = Loader()
        await loader.truncate_insert()

        # Add assertions to verify how empty responses are handled
        # Example: assert await loader.get_data_count() == 0

@pytest.mark.asyncio
async def test_business_rule_altitude_category():
    row = {'baro_altitude': 2500, 'on_ground': False}
    result = Loader.apply_business_rule_altitude_category(row)
    assert result == 'Low Altitude'

@pytest.mark.asyncio
async def test_business_rule_speed_category():
    row = {'velocity': 100, 'on_ground': False}
    result = Loader.apply_business_rule_speed_category(row)
    assert result == 'Approach'