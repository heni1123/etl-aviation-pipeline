import pytest
import httpx
from unittest.mock import AsyncMock
from src.extractors import OpenSkyExtractor, AdsBDBExtractor, RestCountriesExtractor

@pytest.mark.asyncio
async def test_opensky_extractor_happy_path():
    mock_response = {
        "time": 1234567890,
        "states": [
            ["icao24_value", "callsign_value", "origin_country_value", 1234567890, 1234567890, 10.0, 10.0, 1000.0, False, 250.0, 180.0, 0.0, 2000.0, "squawk_value", False, "callsign_iata_value", "airline_name_value", "airline_iata_value", "airline_icao_value", "dep_airport_iata_value"]
        ]
    }
    
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (200, mock_response))) as client:
        extractor = OpenSkyExtractor(client)
        result = await extractor.fetch_states()
        assert result[0]['icao24'] == "icao24_value"
        assert result[0]['callsign'] == "callsign_value"
        assert result[0]['origin_country'] == "origin_country_value"

@pytest.mark.asyncio
async def test_opensky_extractor_empty_response():
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (200, {}))) as client:
        extractor = OpenSkyExtractor(client)
        result = await extractor.fetch_states()
        assert result == []

@pytest.mark.asyncio
async def test_opensky_extractor_null_values():
    mock_response = {
        "time": 1234567890,
        "states": [
            [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        ]
    }
    
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (200, mock_response))) as client:
        extractor = OpenSkyExtractor(client)
        result = await extractor.fetch_states()
        assert result[0]['icao24'] is None
        assert result[0]['callsign'] is None
        assert result[0]['origin_country'] is None

@pytest.mark.asyncio
async def test_adsbdb_extractor_happy_path():
    callsign = "callsign_value"
    mock_response = {
        "response": {
            "airline": {
                "name": "airline_name_value",
                "iata": "airline_iata_value",
                "icao": "airline_icao_value"
            }
        }
    }
    
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (200, mock_response))) as client:
        extractor = AdsBDBExtractor(client)
        result = await extractor.fetch_route_by_callsign(callsign)
        assert result['airline']['name'] == "airline_name_value"
        assert result['airline']['iata'] == "airline_iata_value"

@pytest.mark.asyncio
async def test_adsbdb_extractor_rate_limit():
    callsign = "callsign_value"
    
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (429, {}))) as client:
        extractor = AdsBDBExtractor(client)
        with pytest.raises(httpx.HTTPStatusError):
            await extractor.fetch_route_by_callsign(callsign)

@pytest.mark.asyncio
async def test_rest_countries_extractor_happy_path():
    code = "US"
    mock_response = {
        "success": True,
        "data": {
            "name": "United States",
            "alpha2Code": "US"
        }
    }
    
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (200, mock_response))) as client:
        extractor = RestCountriesExtractor(client)
        result = await extractor.fetch_country_metadata(code)
        assert result['name'] == "United States"
        assert result['alpha2Code'] == "US"

@pytest.mark.asyncio
async def test_rest_countries_extractor_error_response():
    code = "INVALID"
    
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (404, {}))) as client:
        extractor = RestCountriesExtractor(client)
        result = await extractor.fetch_country_metadata(code)
        assert result['success'] is False
        assert 'data' not in result

@pytest.mark.asyncio
async def test_rest_countries_extractor_null_response():
    code = "US"
    
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: (200, {"success": True, "data": None}))) as client:
        extractor = RestCountriesExtractor(client)
        result = await extractor.fetch_country_metadata(code)
        assert result['data'] is None