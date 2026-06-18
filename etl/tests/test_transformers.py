import pytest
import httpx
from unittest.mock import AsyncMock
from src.transformers import Transformer  # Assuming the Transformer class is defined in src/transformers.py

@pytest.mark.asyncio
async def test_altitude_category():
    transformer = Transformer()
    
    test_cases = [
        {'baro_altitude': None, 'on_ground': True, 'expected': 'Ground'},
        {'baro_altitude': 1000, 'on_ground': False, 'expected': 'Low Altitude'},
        {'baro_altitude': 5000, 'on_ground': False, 'expected': 'Mid Altitude'},
        {'baro_altitude': 10000, 'on_ground': False, 'expected': 'Cruise Altitude'},
        {'baro_altitude': 13000, 'on_ground': False, 'expected': 'High Altitude'},
    ]
    
    for case in test_cases:
        result = transformer.apply_business_rule(case, 'altitude_category')
        assert result == case['expected']

@pytest.mark.asyncio
async def test_speed_category():
    transformer = Transformer()
    
    test_cases = [
        {'velocity': None, 'on_ground': True, 'expected': 'Unknown/Ground'},
        {'velocity': 50, 'on_ground': False, 'expected': 'Taxi/Slow'},
        {'velocity': 100, 'on_ground': False, 'expected': 'Approach'},
        {'velocity': 200, 'on_ground': False, 'expected': 'Climb/Descent'},
        {'velocity': 300, 'on_ground': False, 'expected': 'Cruise'},
    ]
    
    for case in test_cases:
        result = transformer.apply_business_rule(case, 'speed_category')
        assert result == case['expected']

@pytest.mark.asyncio
async def test_emergency_flag():
    transformer = Transformer()
    
    test_cases = [
        {'squawk': '7700', 'spi': False, 'expected': 'General Emergency'},
        {'squawk': '7600', 'spi': False, 'expected': 'Radio Failure'},
        {'squawk': '7500', 'spi': False, 'expected': 'Hijacking'},
        {'squawk': '2000', 'spi': False, 'expected': 'VFR No Transponder'},
        {'squawk': None, 'spi': True, 'expected': 'Normal'},
        {'squawk': None, 'spi': False, 'expected': 'Normal'},
    ]
    
    for case in test_cases:
        result = transformer.apply_business_rule(case, 'emergency_flag')
        assert result == case['expected']

@pytest.mark.asyncio
async def test_data_quality_flag():
    transformer = Transformer()
    
    test_cases = [
        {'baro_altitude': None, 'velocity': None, 'expected': 'Poor Quality'},
        {'baro_altitude': 1000, 'velocity': 50, 'expected': 'Good Quality'},
        {'baro_altitude': 5000, 'velocity': None, 'expected': 'Poor Quality'},
        {'baro_altitude': None, 'velocity': 100, 'expected': 'Poor Quality'},
    ]
    
    for case in test_cases:
        result = transformer.apply_business_rule(case, 'data_quality_flag')
        assert result == case['expected']