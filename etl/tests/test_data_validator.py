try:
    from validators.data_validator import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock

@pytest.mark.asyncio
async def test_validate_batch_happy_path(sample_records):
    """Test validate_batch with valid input."""
    validator = DataValidator()
    result = await validator.validate_batch(sample_records)
    assert result['total'] == len(sample_records)
    assert result['valid'] > 0
    assert result['invalid'] == 0
    assert result['failed_records'] == []

@pytest.mark.asyncio
async def test_validate_batch_empty_input(empty_records):
    """Test validate_batch with empty input."""
    validator = DataValidator()
    result = await validator.validate_batch(empty_records)
    assert result['total'] == 0
    assert result['valid'] == 0
    assert result['invalid'] == 0
    assert result['failed_records'] == []

@pytest.mark.asyncio
async def test_validate_batch_error_handling(invalid_records):
    """Test validate_batch with invalid records."""
    validator = DataValidator()
    result = await validator.validate_batch(invalid_records)
    assert result['total'] == len(invalid_records)
    assert result['valid'] == 0
    assert result['invalid'] == len(invalid_records)
    assert len(result['failed_records']) == len(invalid_records)

def test_validate_record_happy_path():
    """Test validate_record with valid input."""
    validator = DataValidator()
    record = {'baro_altitude': 5000, 'on_ground': False}
    result = validator.validate_record(record)
    assert result.is_valid
    assert result.rule_id == 'BR1'

def test_validate_record_empty_input():
    """Test validate_record with empty input."""
    validator = DataValidator()
    record = {}
    result = validator.validate_record(record)
    assert not result.is_valid
    assert result.rule_id == 'BR1'

def test_validate_record_error_handling():
    """Test validate_record with invalid input."""
    validator = DataValidator()
    record = {'baro_altitude': None, 'on_ground': True}
    result = validator.validate_record(record)
    assert not result.is_valid
    assert result.rule_id == 'BR1'

def test_apply_rule_happy_path():
    """Test _apply_rule with valid rule ID."""
    validator = DataValidator()
    record = {'baro_altitude': 5000}
    result = validator._apply_rule(record, 'BR1')
    assert result.is_valid

def test_apply_rule_invalid_rule_id():
    """Test _apply_rule with invalid rule ID."""
    validator = DataValidator()
    record = {'baro_altitude': 5000}
    result = validator._apply_rule(record, 'INVALID_RULE')
    assert result is None

def test_validate_br1_happy_path():
    """Test _validate_br1 with valid altitude."""
    validator = DataValidator()
    record = {'baro_altitude': 5000, 'on_ground': False}
    result = validator._validate_br1(record)
    assert result.is_valid
    assert result.rule_id == 'BR1'

def test_validate_br1_on_ground():
    """Test _validate_br1 when on_ground is True."""
    validator = DataValidator()
    record = {'baro_altitude': 5000, 'on_ground': True}
    result = validator._validate_br1(record)
    assert not result.is_valid
    assert result.rule_id == 'BR1'

def test_validate_br3_happy_path():
    """Test _validate_br3 with valid velocity."""
    validator = DataValidator()
    record = {'velocity': 100, 'on_ground': False}
    result = validator._validate_br3(record)
    assert result.is_valid
    assert result.rule_id == 'BR3'

def test_validate_br3_on_ground():
    """Test _validate_br3 when on_ground is True."""
    validator = DataValidator()
    record = {'velocity': 100, 'on_ground': True}
    result = validator._validate_br3(record)
    assert not result.is_valid
    assert result.rule_id == 'BR3'

def test_validate_br4_happy_path():
    """Test _validate_br4 with valid squawk."""
    validator = DataValidator()
    record = {'squawk': '7700'}
    result = validator._validate_br4(record)
    assert result.is_valid
    assert result.rule_id == 'BR4'

def test_validate_br4_normal_case():
    """Test _validate_br4 with normal squawk."""
    validator = DataValidator()
    record = {'squawk': '2000'}
    result = validator._validate_br4(record)
    assert result.is_valid
    assert result.rule_id == 'BR4'

def test_validate_br5_happy_path():
    """Test _validate_br5 with complete data."""
    validator = DataValidator()
    record = {
        'icao24': 'abcd',
        'callsign': 'test',
        'latitude': 10.0,
        'longitude': 20.0,
        'baro_altitude': 5000
    }
    result = validator._validate_br5(record)
    assert result.is_valid
    assert result.rule_id == 'BR5'

def test_validate_br5_missing_data():
    """Test _validate_br5 with missing required fields."""
    validator = DataValidator()
    record = {
        'icao24': 'abcd',
        'callsign': 'test',
        'latitude': None,
        'longitude': 20.0,
        'baro_altitude': 5000
    }
    result = validator._validate_br5(record)
    assert not result.is_valid
    assert result.rule_id == 'BR5'