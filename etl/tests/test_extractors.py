import pytest
import httpx
from unittest.mock import AsyncMock
from src.extractors import OpenSkyExtractor, AdsBDBExtractor, RestCountriesExtractor

@pytest.mark.asyncio
async def test_opensky_extractor_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"time": 1234567890, "states": [["icao24_value", "callsign_value", "origin_country_value", 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250.0, 180.0, 0.0, 2000, "squawk_value", False, "callsign_iata_value", "airline_name_value", "airline_iata_value", "airline_icao_value", "dep_airport_iata_value", "arr_airport_iata_value", "flight_number_value", "departure_time_value", "arrival_time_value", "status_value"]]},
        )
        extractor = OpenSkyExtractor()
        data = await extractor.fetch_data()
        assert data['states'][0][0] == "icao24_value"
        assert data['states'][0][1] == "callsign_value"

@pytest.mark.asyncio
async def test_opensky_extractor_edge_cases():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"time": 1234567890, "states": []},
        )
        extractor = OpenSkyExtractor()
        data = await extractor.fetch_data()
        assert data['states'] == []

@pytest.mark.asyncio
async def test_adsbdb_extractor_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://api.adsbdb.com/v0/callsign/callsign_value",
            json={"response": {"airline": "airline_name_value", "flight": "flight_number_value"}},
        )
        extractor = AdsBDBExtractor()
        data = await extractor.fetch_data("callsign_value")
        assert data['response']['airline'] == "airline_name_value"

@pytest.mark.asyncio
async def test_adsbdb_extractor_edge_cases():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://api.adsbdb.com/v0/callsign/callsign_value",
            json={"response": None},
        )
        extractor = AdsBDBExtractor()
        data = await extractor.fetch_data("callsign_value")
        assert data['response'] is None

@pytest.mark.asyncio
async def test_rest_countries_extractor_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://restcountries.com/v3.1/alpha/US",
            json={"success": True, "data": {"name": "United States", "alpha2Code": "US"}},
        )
        extractor = RestCountriesExtractor()
        data = await extractor.fetch_data("US")
        assert data['data']['name'] == "United States"

@pytest.mark.asyncio
async def test_rest_countries_extractor_edge_cases():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://restcountries.com/v3.1/alpha/US",
            json={"success": False, "errors": ["Country not found"]},
        )
        extractor = RestCountriesExtractor()
        data = await extractor.fetch_data("US")
        assert not data['success']
        assert "Country not found" in data['errors']