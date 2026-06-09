import pytest
import httpx
from unittest.mock import patch
from src.extractors import OpenSkyExtractor, AdsBDBExtractor, RestCountriesExtractor

@pytest.mark.asyncio
async def test_opensky_extractor_happy_path():
    mock_response = {
        "time": 1609459200,
        "states": [
            ["icao24_value", "callsign_value", "origin_country_value", 1609459200, 1609459260, 10.0, 20.0, 1000.0, False, 300.0, 180.0, 0.0, 2000.0, "squawk_value", False, "callsign_iata_value", "airline_name_value", "airline_iata_value", "airline_icao_value", "dep_airport_iata_value", "arr_airport_iata_value", "flight_number_value"]
        ]
    }
    
    async with httpx.AsyncClient() as client:
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            extractor = OpenSkyExtractor(client)
            data = await extractor.fetch_positions()
            assert data[0]['icao24'] == 'icao24_value'
            assert data[0]['callsign'] == 'callsign_value'
            assert data[0]['origin_country'] == 'origin_country_value'

@pytest.mark.asyncio
async def test_opensky_extractor_empty_response():
    mock_response = {
        "time": 1609459200,
        "states": []
    }
    
    async with httpx.AsyncClient() as client:
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            extractor = OpenSkyExtractor(client)
            data = await extractor.fetch_positions()
            assert data == []

@pytest.mark.asyncio
async def test_opensky_extractor_null_values():
    mock_response = {
        "time": 1609459200,
        "states": [
            ["icao24_value", None, "origin_country_value", 1609459200, 1609459260, 10.0, 20.0, 1000.0, False, 300.0, 180.0, 0.0, 2000.0, "squawk_value", False, None, None, None, None, None, None, None]
        ]
    }
    
    async with httpx.AsyncClient() as client:
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            extractor = OpenSkyExtractor(client)
            data = await extractor.fetch_positions()
            assert data[0]['callsign'] is None

@pytest.mark.asyncio
async def test_adsbdb_extractor_happy_path():
    mock_response = {
        "response": {
            "callsign": "callsign_value",
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
            data = await extractor.fetch_route_by_callsign("callsign_value")
            assert data['callsign'] == 'callsign_value'
            assert data['airline']['name'] == 'airline_name_value'

@pytest.mark.asyncio
async def test_adsbdb_extractor_rate_limit():
    async with httpx.AsyncClient() as client:
        with patch('httpx.AsyncClient.get', side_effect=httpx.HTTPStatusError("Rate limit exceeded", request=None)):
            extractor = AdsBDBExtractor(client)
            with pytest.raises(httpx.HTTPStatusError):
                await extractor.fetch_route_by_callsign("callsign_value")

@pytest.mark.asyncio
async def test_rest_countries_extractor_happy_path():
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
            data = await extractor.fetch_country_metadata("US")
            assert data['cca2'] == 'US'
            assert data['capital'] == 'Washington, D.C.'

@pytest.mark.asyncio
async def test_rest_countries_extractor_empty_response():
    async with httpx.AsyncClient() as client:
        with patch('httpx.AsyncClient.get', return_value={}):
            extractor = RestCountriesExtractor(client)
            data = await extractor.fetch_country_metadata("US")
            assert data == {}

@pytest.mark.asyncio
async def test_rest_countries_extractor_null_values():
    mock_response = {
        "tld": None,
        "cca2": None,
        "ccn3": None,
        "cca3": None,
        "cioc": None,
        "independent": None,
        "status": None,
        "unMember": None,
        "idd": None,
        "capital": None
    }
    
    async with httpx.AsyncClient() as client:
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            extractor = RestCountriesExtractor(client)
            data = await extractor.fetch_country_metadata("US")
            assert data['tld'] is None
            assert data['capital'] is None