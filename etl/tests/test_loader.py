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
            json={"time": 1234567890, "states": [["icao24_value", "callsign_value", "origin_country_value", 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250.0, 180.0, 0.0, 1000, "squawk_value", False, "callsign_iata_value", "airline_name_value", "airline_iata_value", "airline_icao_value", "dep_airport_iata_value", "arr_airport_iata_value", "altitude_category_value", "speed_category_value"]]},
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
            json={"time": 1234567890, "states": [["icao24_value", None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]},
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
        # Add assertions to verify handling of empty response

@pytest.mark.asyncio
async def test_business_rule_altitude_category():
    row = {"baro_altitude": None, "on_ground": True}
    result = Loader.apply_business_rule_altitude_category(row)
    assert result == "Ground"

    row = {"baro_altitude": 2500, "on_ground": False}
    result = Loader.apply_business_rule_altitude_category(row)
    assert result == "Low Altitude"

    row = {"baro_altitude": 8000, "on_ground": False}
    result = Loader.apply_business_rule_altitude_category(row)
    assert result == "Mid Altitude"

    row = {"baro_altitude": 13000, "on_ground": False}
    result = Loader.apply_business_rule_altitude_category(row)
    assert result == "High Altitude"

@pytest.mark.asyncio
async def test_business_rule_speed_category():
    row = {"velocity": None, "on_ground": True}
    result = Loader.apply_business_rule_speed_category(row)
    assert result == "Unknown/Ground"

    row = {"velocity": 150, "on_ground": False}
    result = Loader.apply_business_rule_speed_category(row)
    assert result == "Normal Speed"

    row = {"velocity": 0, "on_ground": True}
    result = Loader.apply_business_rule_speed_category(row)
    assert result == "Unknown/Ground"