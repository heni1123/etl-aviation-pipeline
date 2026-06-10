import pytest
import httpx
from unittest.mock import patch
from src.extractors import OpenSkyExtractor, AdsBDBExtractor, RestCountriesExtractor

@pytest.mark.asyncio
async def test_opensky_extractor_happy_path():
    mock_response = {
        "time": 1234567890,
        "states": [
            ["icao24_value", "callsign_value", "origin_country_value", 1234567890, 1234567890, 10.0, 10.0, 1000.0, False, 250.0, 180.0, 0.0, 2000.0, "squawk_value", False, "callsign_iata_value", "airline_name_value", "airline_iata_value", "airline_icao_value", "dep_airport_iata_value", "arr_airport_iata_value", "flight_number_value", "departure_time_value", "arrival_time_value"]
        ]
    }
    
    async with httpx.AsyncClient() as client:
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            extractor = OpenSkyExtractor(client)
            data = await extractor.fetch_positions()
            assert data['icao24'] == 'icao24_value'
            assert data['callsign'] == 'callsign_value'
            assert data['origin_country'] == 'origin_country_value'

@pytest.mark.asyncio
async def test_opensky_extractor_null_values():
    mock_response = {
        "time": 1234567890,
        "states": [
            [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        ]
    }
    
    async with httpx.AsyncClient() as client:
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            extractor = OpenSkyExtractor(client)
            data = await extractor.fetch_positions()
            assert data['icao24'] is None
            assert data['callsign'] is None
            assert data['origin_country'] is None

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
    
    async with httpx.AsyncClient() as client:
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            extractor = AdsBDBExtractor(client)
            data = await extractor.fetch_route_by_callsign(callsign)
            assert data['airline_name'] == 'airline_name_value'
            assert data['airline_iata'] == 'airline_iata_value'
            assert data['airline_icao'] == 'airline_icao_value'

@pytest.mark.asyncio
async def test_adsbdb_extractor_empty_response():
    callsign = "callsign_value"
    mock_response = {
        "response": {}
    }
    
    async with httpx.AsyncClient() as client:
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            extractor = AdsBDBExtractor(client)
            data = await extractor.fetch_route_by_callsign(callsign)
            assert data['airline_name'] is None
            assert data['airline_iata'] is None
            assert data['airline_icao'] is None

@pytest.mark.asyncio
async def test_rest_countries_extractor_happy_path():
    code = "US"
    mock_response = {
        "tld": [".us"],
        "cca2": "US",
        "ccn3": "840",
        "cca3": "USA",
        "cioc": "USA",
        "independent": True,
        "status": "officially assigned",
        "unMember": True,
        "idd": {"root": "+1", "suffixes": ["202"]},
        "capital": "Washington, D.C."
    }
    
    async with httpx.AsyncClient() as client:
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            extractor = RestCountriesExtractor(client)
            data = await extractor.fetch_country_metadata(code)
            assert data['capital'] == 'Washington, D.C.'
            assert data['cca2'] == 'US'
            assert data['independent'] is True

@pytest.mark.asyncio
async def test_rest_countries_extractor_rate_limit():
    code = "US"
    mock_response = httpx.Response(status_code=429)
    
    async with httpx.AsyncClient() as client:
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            extractor = RestCountriesExtractor(client)
            with pytest.raises(httpx.HTTPStatusError):
                await extractor.fetch_country_metadata(code)