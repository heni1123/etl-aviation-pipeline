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
            json={"time": 1234567890, "states": [["icao24", "callsign", "origin_country", 0, 0, 0, 0, 0, 0]]}
        )
        extractor = OpenSkyExtractor()
        result = await extractor.fetch_positions()
        assert result is not None
        assert len(result) > 0

@pytest.mark.asyncio
async def test_opensky_extractor_empty_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"time": 1234567890, "states": []}
        )
        extractor = OpenSkyExtractor()
        result = await extractor.fetch_positions()
        assert result == []

@pytest.mark.asyncio
async def test_opensky_extractor_null_values():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://opensky-network.org/api/states/all",
            json={"time": 1234567890, "states": [[None, None, None, None, None, None, None, None, None]]}
        )
        extractor = OpenSkyExtractor()
        result = await extractor.fetch_positions()
        assert result is not None
        assert all(value is None for value in result[0].values())

@pytest.mark.asyncio
async def test_adsbdb_extractor_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://api.adsbdb.com/v0/callsign/ABC123",
            json={"response": {"callsign": "ABC123", "route": "Route Info"}}
        )
        extractor = AdsBDBExtractor()
        result = await extractor.fetch_callsign("ABC123")
        assert result is not None
        assert result['callsign'] == "ABC123"

@pytest.mark.asyncio
async def test_adsbdb_extractor_empty_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://api.adsbdb.com/v0/callsign/ABC123",
            json={"response": {}}
        )
        extractor = AdsBDBExtractor()
        result = await extractor.fetch_callsign("ABC123")
        assert result == {}

@pytest.mark.asyncio
async def test_adsbdb_extractor_rate_limit():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://api.adsbdb.com/v0/callsign/ABC123",
            status_code=429,
            json={"error": "Rate limit exceeded"}
        )
        extractor = AdsBDBExtractor()
        with pytest.raises(httpx.HTTPStatusError):
            await extractor.fetch_callsign("ABC123")

@pytest.mark.asyncio
async def test_rest_countries_extractor_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://restcountries.com/v3.1/alpha/FR",
            json={"tld": [".fr"], "cca2": "FR", "ccn3": "250", "cca3": "FRA", "cioc": "FRA", "independent": True, "status": "officially assigned", "unMember": True, "idd": {"root": "+33", "suffixes": []}, "capital": "Paris"}
        )
        extractor = RestCountriesExtractor()
        result = await extractor.fetch_country_metadata("FR")
        assert result is not None
        assert result['cca2'] == "FR"

@pytest.mark.asyncio
async def test_rest_countries_extractor_empty_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://restcountries.com/v3.1/alpha/FR",
            json={}
        )
        extractor = RestCountriesExtractor()
        result = await extractor.fetch_country_metadata("FR")
        assert result == {}

@pytest.mark.asyncio
async def test_rest_countries_extractor_null_values():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            method="GET",
            url="https://restcountries.com/v3.1/alpha/FR",
            json={"tld": [None], "cca2": None, "ccn3": None, "cca3": None, "cioc": None, "independent": None, "status": None, "unMember": None, "idd": None, "capital": None}
        )
        extractor = RestCountriesExtractor()
        result = await extractor.fetch_country_metadata("FR")
        assert result is not None
        assert all(value is None for value in result.values())