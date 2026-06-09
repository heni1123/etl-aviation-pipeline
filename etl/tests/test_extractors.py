import pytest
import httpx
from unittest.mock import patch
from extractors import OpenSkyExtractor, AdsBDBExtractor, RestCountriesExtractor

@pytest.mark.asyncio
async def test_opensky_extractor_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"time": 1234567890, "states": [["icao24", "callsign", "origin_country", 1234567890, 1234567890, 10.0, 10.0, 1000, False, 250.0, 180.0, 0.0, 1000, "squawk", False, "callsign_iata", "airline_name", "airline_iata", "airline_icao", "dep_airport_iata"]]}
        )
        extractor = OpenSkyExtractor()
        result = await extractor.extract()
        assert result is not None

@pytest.mark.asyncio
async def test_opensky_extractor_empty_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"time": 1234567890, "states": []}
        )
        extractor = OpenSkyExtractor()
        result = await extractor.extract()
        assert result == []

@pytest.mark.asyncio
async def test_adsbdb_extractor_happy_path():
    callsign = "ABC123"
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url=f"https://api.adsbdb.com/v0/callsign/{callsign}",
            json={"response": {"icao24": "icao24", "callsign": callsign, "origin_country": "USA"}}
        )
        extractor = AdsBDBExtractor()
        result = await extractor.extract(callsign)
        assert result['callsign'] == callsign

@pytest.mark.asyncio
async def test_adsbdb_extractor_rate_limit():
    callsign = "ABC123"
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url=f"https://api.adsbdb.com/v0/callsign/{callsign}",
            status_code=429,
            json={"error": "Rate limit exceeded"}
        )
        extractor = AdsBDBExtractor()
        with pytest.raises(httpx.HTTPStatusError):
            await extractor.extract(callsign)

@pytest.mark.asyncio
async def test_rest_countries_extractor_happy_path():
    origin_country = "USA"
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url=f"https://restcountries.com/v3.1/alpha/{origin_country}",
            json=[{"name": {"common": "United States"}, "cca2": "US", "capital": "Washington, D.C.", "region": "Americas", "subregion": "North America", "area": 9372610, "population": 331002651, "continents": ["North America"]}]
        )
        extractor = RestCountriesExtractor()
        result = await extractor.extract(origin_country)
        assert result['name'] == "United States"

@pytest.mark.asyncio
async def test_rest_countries_extractor_empty_response():
    origin_country = "USA"
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url=f"https://restcountries.com/v3.1/alpha/{origin_country}",
            json=[]
        )
        extractor = RestCountriesExtractor()
        result = await extractor.extract(origin_country)
        assert result == []