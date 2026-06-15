import pytest
import httpx
from unittest.mock import AsyncMock
from src.extractors import OpenSkyExtractor, AdsBDBExtractor, RestCountriesExtractor

@pytest.mark.asyncio
async def test_opensky_extractor_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://opensky-network.org/api/states/all',
            method='GET',
            json={'time': 1234567890, 'states': [['icao24_value', 'callsign_value', 'origin_country_value', 1234567890, 1234567890, 10.0, 20.0, 1000, False, 300, 180, 0, 5000, 'squawk_value', False, 'callsign_iata_value', 'airline_name_value', 'airline_iata_value', 'airline_icao_value', 'dep_airport_iata_value', 'arr_airport_iata_value', 'flight_number_value', 'departure_time_value', 'arrival_time_value']]},
        )
        extractor = OpenSkyExtractor()
        data = await extractor.fetch_data()
        assert data['states'][0][0] == 'icao24_value'

@pytest.mark.asyncio
async def test_opensky_extractor_empty_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://opensky-network.org/api/states/all',
            method='GET',
            json={'time': 1234567890, 'states': []},
        )
        extractor = OpenSkyExtractor()
        data = await extractor.fetch_data()
        assert data['states'] == []

@pytest.mark.asyncio
async def test_opensky_extractor_rate_limit():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://opensky-network.org/api/states/all',
            method='GET',
            status_code=429,
            json={'error': 'Rate limit exceeded'},
        )
        extractor = OpenSkyExtractor()
        with pytest.raises(httpx.HTTPStatusError):
            await extractor.fetch_data()

@pytest.mark.asyncio
async def test_adsbdb_extractor_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://api.adsbdb.com/v0/callsign/callsign_value',
            method='GET',
            json={'response': {'airline': 'airline_name_value', 'flight': 'flight_number_value'}},
        )
        extractor = AdsBDBExtractor()
        data = await extractor.fetch_data('callsign_value')
        assert data['response']['airline'] == 'airline_name_value'

@pytest.mark.asyncio
async def test_adsbdb_extractor_empty_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://api.adsbdb.com/v0/callsign/callsign_value',
            method='GET',
            json={'response': {}},
        )
        extractor = AdsBDBExtractor()
        data = await extractor.fetch_data('callsign_value')
        assert data['response'] == {}

@pytest.mark.asyncio
async def test_restcountries_extractor_happy_path():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://restcountries.com/v3.1/alpha/US',
            method='GET',
            json={'success': True, 'data': {'name': 'United States', 'alpha2Code': 'US'}},
        )
        extractor = RestCountriesExtractor()
        data = await extractor.fetch_data('US')
        assert data['data']['name'] == 'United States'

@pytest.mark.asyncio
async def test_restcountries_extractor_empty_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://restcountries.com/v3.1/alpha/US',
            method='GET',
            json={'success': True, 'data': {}},
        )
        extractor = RestCountriesExtractor()
        data = await extractor.fetch_data('US')
        assert data['data'] == {}

@pytest.mark.asyncio
async def test_restcountries_extractor_error_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(
            url='https://restcountries.com/v3.1/alpha/XX',
            method='GET',
            status_code=404,
            json={'success': False, 'errors': ['Country not found']},
        )
        extractor = RestCountriesExtractor()
        with pytest.raises(httpx.HTTPStatusError):
            await extractor.fetch_data('XX')