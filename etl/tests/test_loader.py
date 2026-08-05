import pytest
import httpx
from unittest.mock import patch
from your_etl_module import Loader  # Adjust the import based on your actual module structure

@pytest.mark.asyncio
async def test_truncate_insert_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://opensky-network.org/api/states/all',
            method='GET',
            json={'time': 1234567890, 'states': [['icao24_example', 'callsign_example', 'origin_country_example', 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 1000, 'squawk_example', False, 'callsign_iata_example', 'airline_name_example', 'airline_iata_example', 'airline_icao_example', 'dep_airport_iata_example', 'arr_airport_iata_example', 'flight_number_example', 'departure_time_example', 'arrival_time_example', 'duration_example']]},
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
            json={'time': 1234567890, 'states': [['icao24_example', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]},
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
    row = {'baro_altitude': 2500, 'on_ground': False}
    category = Loader.get_altitude_category(row)
    assert category == 'Low Altitude'

    row = {'baro_altitude': 8000, 'on_ground': False}
    category = Loader.get_altitude_category(row)
    assert category == 'Cruise Altitude'

    row = {'baro_altitude': None, 'on_ground': True}
    category = Loader.get_altitude_category(row)
    assert category == 'Ground'

@pytest.mark.asyncio
async def test_business_rule_speed_category():
    row = {'velocity': 200, 'on_ground': False}
    category = Loader.get_speed_category(row)
    assert category == 'Normal Speed'

    row = {'velocity': None, 'on_ground': True}
    category = Loader.get_speed_category(row)
    assert category == 'Unknown/Ground'