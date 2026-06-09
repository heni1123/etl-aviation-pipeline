import pytest
import httpx
from unittest.mock import patch
from your_loader_module import Loader  # Replace with the actual module name

@pytest.mark.asyncio
async def test_truncate_insert_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"time": 1234567890, "states": [["icao24_value", "callsign_value", "origin_country_value", 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 1000, "squawk_value", False, "callsign_iata_value", "airline_name_value", "airline_iata_value", "airline_icao_value", "dep_airport_iata_value", "arr_airport_iata_value", "flight_number_value", "departure_time_value", "arrival_time_value", "status_value"]]},
        )
        loader = Loader()
        await loader.load_data()
        # Add assertions to verify data in the database

@pytest.mark.asyncio
async def test_truncate_insert_null_values():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"time": 1234567890, "states": [["icao24_value", None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]},
        )
        loader = Loader()
        await loader.load_data()
        # Add assertions to verify handling of null values in the database

@pytest.mark.asyncio
async def test_truncate_insert_rate_limit():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            status_code=429,
            json={"error": "Rate limit exceeded"},
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
            json={"time": 1234567890, "states": []},
        )
        loader = Loader()
        await loader.load_data()
        # Add assertions to verify handling of empty response in the database

@pytest.mark.asyncio
async def test_business_rule_altitude_category():
    row = {"baro_altitude": 2000, "on_ground": False}
    category = Loader.get_altitude_category(row)
    assert category == "Low Altitude"

@pytest.mark.asyncio
async def test_business_rule_speed_category():
    row = {"velocity": 250, "on_ground": False}
    category = Loader.get_speed_category(row)
    assert category == "Cruise Speed"  # Adjust based on actual logic

@pytest.mark.asyncio
async def test_business_rule_altitude_category_on_ground():
    row = {"baro_altitude": None, "on_ground": True}
    category = Loader.get_altitude_category(row)
    assert category == "Ground"

@pytest.mark.asyncio
async def test_business_rule_speed_category_unknown():
    row = {"velocity": None, "on_ground": "Unknown/Ground"}
    category = Loader.get_speed_category(row)
    assert category == "Unknown/Ground"  # Adjust based on actual logic