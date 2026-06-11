import pytest
import httpx
from unittest.mock import patch
from your_etl_module import Loader  # Adjust the import based on your actual module structure

@pytest.mark.asyncio
async def test_truncate_insert_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"time": 1234567890, "states": [["icao24", "callsign", "origin_country", 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 1000, "squawk", False, "callsign_iata", "airline_name", "airline_iata", "airline_icao", "dep_airport_iata"]]}
        )
        loader = Loader()
        await loader.load_data()
        # Add assertions to verify data was loaded correctly

@pytest.mark.asyncio
async def test_truncate_insert_null_values():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"time": 1234567890, "states": [["icao24", None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]}
        )
        loader = Loader()
        await loader.load_data()
        # Add assertions to verify handling of null values

@pytest.mark.asyncio
async def test_truncate_insert_rate_limit():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            status_code=429,
            json={"error": "Rate limit exceeded"}
        )
        loader = Loader()
        with pytest.raises(httpx.HTTPStatusError):
            await loader.load_data()

@pytest.mark.asyncio
async def test_truncate_insert_empty_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"time": 1234567890, "states": []}
        )
        loader = Loader()
        await loader.load_data()
        # Add assertions to verify handling of empty response

@pytest.mark.asyncio
async def test_business_rule_altitude_category():
    row = {"baro_altitude": 2500, "on_ground": False}
    category = Loader.categorize_altitude(row)
    assert category == "Low Altitude"

@pytest.mark.asyncio
async def test_business_rule_speed_category():
    row = {"velocity": 150, "on_ground": False}
    category = Loader.categorize_speed(row)
    assert category == "Cruise Speed"  # Adjust based on actual logic

@pytest.mark.asyncio
async def test_business_rule_altitude_category_ground():
    row = {"baro_altitude": None, "on_ground": True}
    category = Loader.categorize_altitude(row)
    assert category == "Ground"

@pytest.mark.asyncio
async def test_business_rule_speed_category_ground():
    row = {"velocity": None, "on_ground": True}
    category = Loader.categorize_speed(row)
    assert category == "Unknown/Ground"