import pytest
import httpx
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_altitude_category_ground():
    row = {'baro_altitude': None, 'on_ground': True}
    result = categorize_altitude(row)
    assert result == 'Ground'

@pytest.mark.asyncio
async def test_altitude_category_low():
    row = {'baro_altitude': 2500, 'on_ground': False}
    result = categorize_altitude(row)
    assert result == 'Low Altitude'

@pytest.mark.asyncio
async def test_altitude_category_mid():
    row = {'baro_altitude': 5000, 'on_ground': False}
    result = categorize_altitude(row)
    assert result == 'Mid Altitude'

@pytest.mark.asyncio
async def test_altitude_category_cruise():
    row = {'baro_altitude': 12000, 'on_ground': False}
    result = categorize_altitude(row)
    assert result == 'Cruise Altitude'

@pytest.mark.asyncio
async def test_altitude_category_high():
    row = {'baro_altitude': 13000, 'on_ground': False}
    result = categorize_altitude(row)
    assert result == 'High Altitude'

@pytest.mark.asyncio
async def test_speed_category_unknown_ground():
    row = {'velocity': None, 'on_ground': True}
    result = categorize_speed(row)
    assert result == 'Unknown/Ground'

@pytest.mark.asyncio
async def test_speed_category_taxi():
    row = {'velocity': 50, 'on_ground': False}
    result = categorize_speed(row)
    assert result == 'Taxi/Slow'

@pytest.mark.asyncio
async def test_speed_category_approach():
    row = {'velocity': 100, 'on_ground': False}
    result = categorize_speed(row)
    assert result == 'Approach'

@pytest.mark.asyncio
async def test_speed_category_climb():
    row = {'velocity': 200, 'on_ground': False}
    result = categorize_speed(row)
    assert result == 'Climb/Descent'

@pytest.mark.asyncio
async def test_speed_category_cruise():
    row = {'velocity': 300, 'on_ground': False}
    result = categorize_speed(row)
    assert result == 'Cruise'

@pytest.mark.asyncio
async def test_emergency_flag_general_emergency():
    row = {'squawk': '7700', 'spi': False}
    result = flag_emergency(row)
    assert result == 'General Emergency'

@pytest.mark.asyncio
async def test_emergency_flag_radio_failure():
    row = {'squawk': '7600', 'spi': False}
    result = flag_emergency(row)
    assert result == 'Radio Failure'

@pytest.mark.asyncio
async def test_emergency_flag_hijacking():
    row = {'squawk': '7500', 'spi': False}
    result = flag_emergency(row)
    assert result == 'Hijacking'

@pytest.mark.asyncio
async def test_emergency_flag_vfr_no_transponder():
    row = {'squawk': '2000', 'spi': False}
    result = flag_emergency(row)
    assert result == 'VFR No Transponder'

@pytest.mark.asyncio
async def test_emergency_flag_special_purpose():
    row = {'squawk': None, 'spi': True}
    result = flag_emergency(row)
    assert result == 'Special Purpose'

@pytest.mark.asyncio
async def test_emergency_flag_normal():
    row = {'squawk': None, 'spi': False}
    result = flag_emergency(row)
    assert result == 'Normal'

@pytest.mark.asyncio
async def test_data_quality_flag_invalid():
    row = {'icao24': None}
    result = flag_data_quality(row)
    assert result == 'Invalid'

@pytest.mark.asyncio
async def test_data_quality_flag_valid():
    row = {'icao24': 'abc123'}
    result = flag_data_quality(row)
    assert result == 'Valid'

def categorize_altitude(row: dict) -> str:
    return ('Ground' if row.get('baro_altitude') is None or row.get('on_ground') 
            else 'Low Altitude' if row.get('baro_altitude') <= 3000 
            else 'Mid Altitude' if row.get('baro_altitude') <= 7500 
            else 'Cruise Altitude' if row.get('baro_altitude') <= 12500 
            else 'High Altitude')

def categorize_speed(row: dict) -> str:
    return ('Unknown/Ground' if row.get('velocity') is None or row.get('on_ground') 
            else 'Taxi/Slow' if row.get('velocity') <= 80 
            else 'Approach' if row.get('velocity') <= 150 
            else 'Climb/Descent' if row.get('velocity') <= 230 
            else 'Cruise')

def flag_emergency(row: dict) -> str:
    return ('General Emergency' if row.get('squawk') == '7700' 
            else 'Radio Failure' if row.get('squawk') == '7600' 
            else 'Hijacking' if row.get('squawk') == '7500' 
            else 'VFR No Transponder' if row.get('squawk') == '2000' 
            else 'Special Purpose' if row.get('spi') 
            else 'Normal')

def flag_data_quality(row: dict) -> str:
    return 'Invalid' if row.get('icao24') is None else 'Valid'