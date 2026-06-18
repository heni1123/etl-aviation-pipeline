import pytest
import httpx
from unittest.mock import patch
from typing import Dict, Any

@pytest.mark.asyncio
async def test_altitude_category():
    from transformers import transform_row  # Assuming the function is in transformers module

    test_cases = [
        {'baro_altitude': None, 'on_ground': True, 'expected': 'Ground'},
        {'baro_altitude': 1500, 'on_ground': False, 'expected': 'Low Altitude'},
        {'baro_altitude': 5000, 'on_ground': False, 'expected': 'Mid Altitude'},
        {'baro_altitude': 10000, 'on_ground': False, 'expected': 'Cruise Altitude'},
        {'baro_altitude': 13000, 'on_ground': False, 'expected': 'High Altitude'},
    ]

    for case in test_cases:
        result = transform_row(case)
        assert result['altitude_category'] == case['expected']

@pytest.mark.asyncio
async def test_speed_category():
    from transformers import transform_row  # Assuming the function is in transformers module

    test_cases = [
        {'velocity': None, 'on_ground': True, 'expected': 'Unknown/Ground'},
        {'velocity': 50, 'on_ground': False, 'expected': 'Taxi/Slow'},
        {'velocity': 120, 'on_ground': False, 'expected': 'Approach'},
        {'velocity': 200, 'on_ground': False, 'expected': 'Climb/Descent'},
        {'velocity': 250, 'on_ground': False, 'expected': 'Cruise'},
    ]

    for case in test_cases:
        result = transform_row(case)
        assert result['speed_category'] == case['expected']

@pytest.mark.asyncio
async def test_emergency_flag():
    from transformers import transform_row  # Assuming the function is in transformers module

    test_cases = [
        {'squawk': '7700', 'spi': False, 'expected': 'General Emergency'},
        {'squawk': '7600', 'spi': False, 'expected': 'Radio Failure'},
        {'squawk': '7500', 'spi': False, 'expected': 'Hijacking'},
        {'squawk': '2000', 'spi': False, 'expected': 'VFR No Transponder'},
        {'squawk': None, 'spi': True, 'expected': 'Special Purpose'},
        {'squawk': None, 'spi': False, 'expected': 'Normal'},
    ]

    for case in test_cases:
        result = transform_row(case)
        assert result['emergency_flag'] == case['expected']

@pytest.mark.asyncio
async def test_data_quality_flag():
    from transformers import transform_row  # Assuming the function is in transformers module

    test_cases = [
        {'icao24': 'abc123', 'expected': 'Valid'},
        {'icao24': None, 'expected': 'Invalid'},
    ]

    for case in test_cases:
        result = transform_row(case)
        assert result['data_quality_flag'] == case['expected']