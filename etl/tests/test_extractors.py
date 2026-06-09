import pytest
import httpx
from unittest.mock import AsyncMock
from extractors import OpenSkyExtractor, AdsBDBExtractor, RestCountriesExtractor

@pytest.mark.asyncio
async def test_opensky_extractor_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"time": 1234567890, "states": [["icao24", "callsign", "origin_country", 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 1000, "squawk", False, "callsign_iata", "airline_name", "airline_iata", "airline_icao", "dep_airport_iata", "arr_airport_iata", "flight_number", "departure_time", "arrival_time", "duration"]]}
        )
        extractor = OpenSkyExtractor()
        data = await extractor.extract()
        assert data is not None
        assert len(data) > 0

@pytest.mark.asyncio
async def test_opensky_extractor_empty_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"time": 1234567890, "states": []}
        )
        extractor = OpenSkyExtractor()
        data = await extractor.extract()
        assert data == []

@pytest.mark.asyncio
async def test_adsbdb_extractor_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://api.adsbdb.com/v0/callsign/test_callsign",
            json={"response": {"icao24": "test_icao", "callsign": "test_callsign"}}
        )
        extractor = AdsBDBExtractor()
        data = await extractor.extract("test_callsign")
        assert data is not None
        assert data['callsign'] == "test_callsign"

@pytest.mark.asyncio
async def test_adsbdb_extractor_rate_limit():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://api.adsbdb.com/v0/callsign/test_callsign",
            status_code=429,
            json={"error": "Rate limit exceeded"}
        )
        extractor = AdsBDBExtractor()
        with pytest.raises(httpx.HTTPStatusError):
            await extractor.extract("test_callsign")

@pytest.mark.asyncio
async def test_rest_countries_extractor_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://restcountries.com/v3.1/alpha/test_country",
            json={"name": "Test Country", "cca2": "TC", "capital": "Test City", "region": "Test Region", "subregion": "Test Subregion", "area": 10000, "population": 100000, "continents": ["Test Continent"]}
        )
        extractor = RestCountriesExtractor()
        data = await extractor.extract("test_country")
        assert data is not None
        assert data['name'] == "Test Country"

@pytest.mark.asyncio
async def test_rest_countries_extractor_empty_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://restcountries.com/v3.1/alpha/test_country",
            json={}
        )
        extractor = RestCountriesExtractor()
        data = await extractor.extract("test_country")
        assert data == {}