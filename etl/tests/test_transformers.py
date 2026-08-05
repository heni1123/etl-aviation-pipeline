import pytest
import httpx
from unittest.mock import AsyncMock
from your_module import transform_data  # Replace with actual import

@pytest.mark.asyncio
async def test_altitude_category():
    test_cases = [
        {'baro_altitude': None, 'on_ground': True, 'expected': 'Ground'},
        {'baro_altitude': 1000, 'on_ground': False, 'expected': 'Low Altitude'},
        {'baro_altitude': 5000, 'on_ground': False, 'expected': 'Mid Altitude'},
        {'baro_altitude': 10000, 'on_ground': False, 'expected': 'Cruise Altitude'},
        {'baro_altitude': 13000, 'on_ground': False, 'expected': 'High Altitude'},
    ]
    
    for case in test_cases:
        result = transform_data(case)
        assert result['altitude_category'] == case['expected']

@pytest.mark.asyncio
async def test_speed_category():
    test_cases = [
        {'velocity': None, 'on_ground': 'Unknown/Ground', 'expected': 'Unknown/Ground'},
        {'velocity': 50, 'on_ground': False, 'expected': 'Taxi/Slow'},
        {'velocity': 100, 'on_ground': False, 'expected': 'Approach'},
        {'velocity': 200, 'on_ground': False, 'expected': 'Climb/Descent'},
        {'velocity': 300, 'on_ground': False, 'expected': 'Cruise'},
    ]
    
    for case in test_cases:
        result = transform_data(case)
        assert result['speed_category'] == case['expected']

@pytest.mark.asyncio
async def test_emergency_flag():
    test_cases = [
        {'squawk': '7700', 'spi': False, 'expected': 'General Emergency'},
        {'squawk': '7600', 'spi': False, 'expected': 'Radio Failure'},
        {'squawk': '7500', 'spi': False, 'expected': 'Hijacking'},
        {'squawk': '2000', 'spi': False, 'expected': 'VFR No Transponder'},
        {'squawk': None, 'spi': True, 'expected': 'Normal'},
        {'squawk': '1234', 'spi': True, 'expected': 'Normal'},
    ]
    
    for case in test_cases:
        result = transform_data(case)
        assert result['emergency_flag'] == case['expected']

@pytest.mark.asyncio
async def test_data_quality_flag():
    test_cases = [
        {'icao24': 'abc123', 'callsign': None, 'expected': 'Missing Callsign'},
        {'icao24': 'abc123', 'callsign': 'ABC123', 'expected': 'Valid'},
        {'icao24': None, 'callsign': 'ABC123', 'expected': 'Missing ICAO24'},
    ]
    
    for case in test_cases:
        result = transform_data(case)
        assert result['data_quality_flag'] == case['expected']