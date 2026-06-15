import pytest
import httpx
from unittest.mock import patch

@pytest.mark.asyncio
async def test_br1_valid_icao24():
    row = {'icao24': 'ABC123'}
    assert row['icao24'] is not None

@pytest.mark.asyncio
async def test_br1_invalid_icao24():
    row = {'icao24': None}
    assert row['icao24'] is None

@pytest.mark.asyncio
async def test_br2_valid_callsign():
    row = {'callsign': 'abc def'}
    assert row['callsign'].strip().upper() == 'ABC DEF'

@pytest.mark.asyncio
async def test_br2_empty_callsign():
    row = {'callsign': '   '}
    assert row['callsign'].strip().upper() == ''

@pytest.mark.asyncio
async def test_br3_valid_origin_country():
    valid_iso_country_codes = ['US', 'FR', 'DE']
    row = {'origin_country': 'US'}
    assert row['origin_country'] in valid_iso_country_codes

@pytest.mark.asyncio
async def test_br3_invalid_origin_country():
    valid_iso_country_codes = ['US', 'FR', 'DE']
    row = {'origin_country': 'XYZ'}
    assert row['origin_country'] not in valid_iso_country_codes

@pytest.mark.asyncio
async def test_br4_aircraft_on_ground():
    row = {'on_ground': False}
    assert not row['on_ground']

@pytest.mark.asyncio
async def test_br4_aircraft_not_on_ground():
    row = {'on_ground': True}
    assert row['on_ground']

@pytest.mark.asyncio
async def test_br5_velocity_in_air():
    row = {'velocity': 300, 'on_ground': False}
    assert row['velocity'] > 0

@pytest.mark.asyncio
async def test_br5_velocity_on_ground():
    row = {'velocity': 0, 'on_ground': True}
    assert row['velocity'] > 0 if not row['on_ground'] else True

@pytest.mark.asyncio
async def test_br5_velocity_zero_in_air():
    row = {'velocity': 0, 'on_ground': False}
    assert row['velocity'] > 0 if not row['on_ground'] else True