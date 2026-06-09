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
            json={"time": 1234567890, "states": [["icao24", "callsign", "origin_country", 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250, 180, 0, 5000, "squawk", False, "callsign_iata", "airline_name", "airline_iata", "airline_icao", "dep_airport_iata", "arr_airport_iata", "flight_number", "departure_time", "arrival_time"]]}
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
            url="https://api.adsbdb.com/v0/callsign/test",
            json={"response": {"icao24": "test", "callsign": "TEST", "origin_country": "USA"}}
        )
        extractor = AdsBDBExtractor()
        data = await extractor.extract("test")
        assert data is not None
        assert data['icao24'] == "test"

@pytest.mark.asyncio
async def test_adsbdb_extractor_rate_limit():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://api.adsbdb.com/v0/callsign/test",
            status_code=429,
            json={"error": "Rate limit exceeded"}
        )
        extractor = AdsBDBExtractor()
        with pytest.raises(httpx.HTTPStatusError):
            await extractor.extract("test")

@pytest.mark.asyncio
async def test_rest_countries_extractor_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://restcountries.com/v3.1/alpha/USA",
            json=[{"name": {"common": "United States"}, "cca2": "US", "capital": "Washington, D.C.", "region": "Americas", "subregion": "North America", "area": 9372610, "population": 331002651, "continents": ["North America"]}]
        )
        extractor = RestCountriesExtractor()
        data = await extractor.extract("USA")
        assert data is not None
        assert data['name']['common'] == "United States"

@pytest.mark.asyncio
async def test_rest_countries_extractor_empty_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://restcountries.com/v3.1/alpha/XYZ",
            json=[]
        )
        extractor = RestCountriesExtractor()
        data = await extractor.extract("XYZ")
        assert data == []