import pytest
import httpx
from unittest.mock import AsyncMock
from src.extractors import OpenSkyExtractor, AdsBDBExtractor, RestCountriesExtractor

@pytest.mark.asyncio
async def test_opensky_extractor_happy_path():
    mock_response = {
        "time": 1234567890,
        "states": [
            ["icao24_value", "callsign_value", "origin_country_value", 1234567890, 1234567890, 10.0, 20.0, 1000.0, False, 300.0, 180.0, 0.0, 5000.0, "squawk_value", False, "callsign_iata_value", "airline_name_value", "airline_iata_value", "airline_icao_value", "dep_airport_iata_value", "arr_airport_iata_value", "flight_number_value", "departure_time_value", "arrival_time_value"]
        ]
    }
    
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (200, mock_response))) as client:
        extractor = OpenSkyExtractor(client)
        result = await extractor.fetch_states()
        assert result['states'][0][0] == "icao24_value"
        assert result['states'][0][1] == "callsign_value"

@pytest.mark.asyncio
async def test_opensky_extractor_empty_response():
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (200, {}))) as client:
        extractor = OpenSkyExtractor(client)
        result = await extractor.fetch_states()
        assert result == {}

@pytest.mark.asyncio
async def test_opensky_extractor_rate_limit():
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (429, {"error": "Rate limit exceeded"}))) as client:
        extractor = OpenSkyExtractor(client)
        with pytest.raises(httpx.HTTPStatusError):
            await extractor.fetch_states()

@pytest.mark.asyncio
async def test_adsbdb_extractor_happy_path():
    callsign = "CALLSIGN"
    mock_response = {
        "response": {
            "airline": "airline_name_value",
            "flight": "flight_number_value"
        }
    }
    
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (200, mock_response))) as client:
        extractor = AdsBDBExtractor(client)
        result = await extractor.fetch_callsign_data(callsign)
        assert result['response']['airline'] == "airline_name_value"

@pytest.mark.asyncio
async def test_adsbdb_extractor_empty_response():
    callsign = "CALLSIGN"
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (200, {}))) as client:
        extractor = AdsBDBExtractor(client)
        result = await extractor.fetch_callsign_data(callsign)
        assert result == {}

@pytest.mark.asyncio
async def test_adsbdb_extractor_rate_limit():
    callsign = "CALLSIGN"
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (429, {"error": "Rate limit exceeded"}))) as client:
        extractor = AdsBDBExtractor(client)
        with pytest.raises(httpx.HTTPStatusError):
            await extractor.fetch_callsign_data(callsign)

@pytest.mark.asyncio
async def test_rest_countries_extractor_happy_path():
    code = "FR"
    mock_response = {
        "success": True,
        "data": {
            "name": "France",
            "alpha2Code": "FR"
        }
    }
    
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (200, mock_response))) as client:
        extractor = RestCountriesExtractor(client)
        result = await extractor.fetch_country_data(code)
        assert result['data']['name'] == "France"

@pytest.mark.asyncio
async def test_rest_countries_extractor_empty_response():
    code = "FR"
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (200, {}))) as client:
        extractor = RestCountriesExtractor(client)
        result = await extractor.fetch_country_data(code)
        assert result == {}

@pytest.mark.asyncio
async def test_rest_countries_extractor_rate_limit():
    code = "FR"
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (429, {"error": "Rate limit exceeded"}))) as client:
        extractor = RestCountriesExtractor(client)
        with pytest.raises(httpx.HTTPStatusError):
            await extractor.fetch_country_data(code)