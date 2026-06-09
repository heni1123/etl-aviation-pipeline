import pytest
import httpx
from unittest.mock import patch
from your_etl_module import Loader  # Adjust the import based on your actual module structure

@pytest.mark.asyncio
async def test_br1_unique_identifier():
    async with httpx.MockTransport() as transport:
        transport.add_response(json={"states": [{"icao24": "abcd12", "callsign": "ABC123", "origin_country": "USA", "time_position": 1609459200}]})
        loader = Loader()
        await loader.load_data()
        result = await loader.fetch_data()
        assert result[0]['icao24'] == "abcd12"

@pytest.mark.asyncio
async def test_br2_callsign_cleaning():
    async with httpx.MockTransport() as transport:
        transport.add_response(json={"states": [{"icao24": "abcd12", "callsign": " abc123 ", "origin_country": "USA", "time_position": 1609459200}]})
        loader = Loader()
        await loader.load_data()
        result = await loader.fetch_data()
        assert result[0]['callsign'] == "ABC123"

@pytest.mark.asyncio
async def test_br3_origin_country():
    async with httpx.MockTransport() as transport:
        transport.add_response(json={"states": [{"icao24": "abcd12", "callsign": "ABC123", "origin_country": "USA", "time_position": 1609459200}]})
        loader = Loader()
        await loader.load_data()
        result = await loader.fetch_data()
        assert result[0]['origin_country'] == "USA"

@pytest.mark.asyncio
async def test_br4_time_position():
    async with httpx.MockTransport() as transport:
        transport.add_response(json={"states": [{"icao24": "abcd12", "callsign": "ABC123", "origin_country": "USA", "time_position": 1609459200}]})
        loader = Loader()
        await loader.load_data()
        result = await loader.fetch_data()
        assert result[0]['time_position'] == 1609459200

@pytest.mark.asyncio
async def test_br5_null_values():
    async with httpx.MockTransport() as transport:
        transport.add_response(json={"states": [{"icao24": None, "callsign": None, "origin_country": None, "time_position": None}]})
        loader = Loader()
        await loader.load_data()
        result = await loader.fetch_data()
        assert result[0]['icao24'] is None
        assert result[0]['callsign'] is None
        assert result[0]['origin_country'] is None
        assert result[0]['time_position'] is None

@pytest.mark.asyncio
async def test_br_edge_case_empty_response():
    async with httpx.MockTransport() as transport:
        transport.add_response(json={"states": []})
        loader = Loader()
        await loader.load_data()
        result = await loader.fetch_data()
        assert result == []