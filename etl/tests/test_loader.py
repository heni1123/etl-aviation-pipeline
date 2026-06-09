import pytest
import httpx
from unittest.mock import patch
from loader import Loader  # Assuming the loader class is defined in loader.py

@pytest.mark.asyncio
async def test_truncate_insert_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"states": [["icao24_value", "CALLSIGN", "Country", 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 1000, "squawk", False, "CALLSIGN_IATA", "Airline Name", "Airline IATA", "Airline ICAO", "DEP_AIRPORT_IATA", "ARR_AIRPORT_IATA", "FLIGHT_ID"]]}
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
            json={"states": [["icao24_value", None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]}
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
        with pytest.raises(Exception, match="Rate limit exceeded"):
            await loader.load_data()

@pytest.mark.asyncio
async def test_truncate_insert_empty_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"states": []}
        )
        loader = Loader()
        await loader.load_data()
        # Add assertions to verify handling of empty response

@pytest.mark.asyncio
async def test_business_rule_1():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"states": [["icao24_value", "CALLSIGN", "Country", 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 1000, "squawk", False, "CALLSIGN_IATA", "Airline Name", "Airline IATA", "Airline ICAO", "DEP_AIRPORT_IATA", "ARR_AIRPORT_IATA", "FLIGHT_ID"]]}
        )
        loader = Loader()
        await loader.load_data()
        # Add assertions to verify BR1 logic

@pytest.mark.asyncio
async def test_business_rule_2():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"states": [["icao24_value", " callSign ", "Country", 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 1000, "squawk", False, "CALLSIGN_IATA", "Airline Name", "Airline IATA", "Airline ICAO", "DEP_AIRPORT_IATA", "ARR_AIRPORT_IATA", "FLIGHT_ID"]]}
        )
        loader = Loader()
        await loader.load_data()
        # Add assertions to verify BR2 logic

@pytest.mark.asyncio
async def test_business_rule_3():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"states": [["icao24_value", "CALLSIGN", "US", 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 1000, "squawk", False, "CALLSIGN_IATA", "Airline Name", "Airline IATA", "Airline ICAO", "DEP_AIRPORT_IATA", "ARR_AIRPORT_IATA", "FLIGHT_ID"]]}
        )
        loader = Loader()
        await loader.load_data()
        # Add assertions to verify BR3 logic

@pytest.mark.asyncio
async def test_business_rule_4():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"states": [["icao24_value", "CALLSIGN", "Country", -1, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 1000, "squawk", False, "CALLSIGN_IATA", "Airline Name", "Airline IATA", "Airline ICAO", "DEP_AIRPORT_IATA", "ARR_AIRPORT_IATA", "FLIGHT_ID"]]}
        )
        loader = Loader()
        await loader.load_data()
        # Add assertions to verify BR4 logic