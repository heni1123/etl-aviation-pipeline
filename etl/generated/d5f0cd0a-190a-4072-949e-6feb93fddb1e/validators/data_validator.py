import logging
from typing import List, Dict, Optional, Tuple

class ValidationResult:
    def __init__(self, is_valid: bool, rule_id: str, column: str, message: str, severity: str):
        self.is_valid = is_valid
        self.rule_id = rule_id
        self.column = column
        self.message = message
        self.severity = severity

class DataValidator:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def validate_batch(self, records: List[Dict]) -> Dict[str, Optional[List[Dict]]]:
        total_records = len(records)
        valid_count = 0
        invalid_count = 0
        failed_records = []

        for record in records:
            result = self.validate_record(record)
            if result.is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                failed_records.append(record)
                if result.severity == 'critical':
                    self.logger.error(f"Critical violation: {result.message}")

        return {
            "total": total_records,
            "valid": valid_count,
            "invalid": invalid_count,
            "failed_records": failed_records
        }

    def validate_record(self, record: Dict) -> ValidationResult:
        for rule_id in ['BR1', 'BR3', 'BR4', 'BR5', 'BR6']:
            result = self._apply_rule(record, rule_id)
            if result:
                return result
        return ValidationResult(True, '', '', 'No violations', 'info')

    def _apply_rule(self, record: Dict, rule_id: str) -> Optional[ValidationResult]:
        if rule_id == 'BR1':
            return self._validate_br1(record)
        elif rule_id == 'BR3':
            return self._validate_br3(record)
        elif rule_id == 'BR4':
            return self._validate_br4(record)
        elif rule_id == 'BR5':
            return self._validate_br5(record)
        elif rule_id == 'BR6':
            return self._validate_br6(record)
        return None

    def _validate_br1(self, record: Dict) -> ValidationResult:
        baro_altitude = record.get('baro_altitude')
        on_ground = record.get('on_ground', False)
        if baro_altitude is None or on_ground:
            return ValidationResult(False, 'BR1', 'altitude_category', 'Ground', 'critical')
        elif 0 < baro_altitude <= 3000:
            return ValidationResult(True, 'BR1', 'altitude_category', 'Low Altitude', 'info')
        elif 3000 < baro_altitude <= 7500:
            return ValidationResult(True, 'BR1', 'altitude_category', 'Mid Altitude', 'info')
        elif 7500 < baro_altitude <= 12500:
            return ValidationResult(True, 'BR1', 'altitude_category', 'Cruise Altitude', 'info')
        else:
            return ValidationResult(True, 'BR1', 'altitude_category', 'High Altitude', 'info')

    def _validate_br3(self, record: Dict) -> ValidationResult:
        velocity = record.get('velocity')
        on_ground = record.get('on_ground', False)
        if velocity is None or on_ground:
            return ValidationResult(False, 'BR3', 'speed_category', 'Unknown/Ground', 'critical')
        elif 0 < velocity <= 80:
            return ValidationResult(True, 'BR3', 'speed_category', 'Taxi/Slow', 'info')
        elif 80 < velocity <= 150:
            return ValidationResult(True, 'BR3', 'speed_category', 'Approach', 'info')
        elif 150 < velocity <= 230:
            return ValidationResult(True, 'BR3', 'speed_category', 'Climb/Descent', 'info')
        else:
            return ValidationResult(True, 'BR3', 'speed_category', 'Cruise', 'info')

    def _validate_br4(self, record: Dict) -> ValidationResult:
        squawk = record.get('squawk')
        spi = record.get('spi', False)
        if squawk == '7700':
            return ValidationResult(True, 'BR4', 'emergency_flag', 'General Emergency', 'info')
        elif squawk == '7600':
            return ValidationResult(True, 'BR4', 'emergency_flag', 'Radio Failure', 'info')
        elif squawk == '7500':
            return ValidationResult(True, 'BR4', 'emergency_flag', 'Hijacking', 'info')
        elif squawk == '2000':
            return ValidationResult(True, 'BR4', 'emergency_flag', 'VFR No Transponder', 'info')
        elif spi:
            return ValidationResult(True, 'BR4', 'emergency_flag', 'Special Purpose', 'info')
        else:
            return ValidationResult(True, 'BR4', 'emergency_flag', 'Normal', 'info')

    def _validate_br5(self, record: Dict) -> ValidationResult:
        icao24 = record.get('icao24')
        callsign = record.get('callsign')
        latitude = record.get('latitude')
        longitude = record.get('longitude')
        baro_altitude = record.get('baro_altitude')

        if icao24 and callsign and latitude is not None and longitude is not None and baro_altitude is not None:
            return ValidationResult(True, 'BR5', 'data_quality_flag', 'Complete', 'info')
        elif icao24 and callsign and (latitude is None or longitude is None or baro_altitude is None):
            return ValidationResult(False, 'BR5', 'data_quality_flag', 'Partial', 'warning')
        else:
            return ValidationResult(False, 'BR5', 'data_quality_flag', 'Critical', 'critical')

    def _validate_br6(self, record: Dict) -> ValidationResult:
        # Placeholder for rule BR6 implementation
        return ValidationResult(True, 'BR6', 'route_type', 'Not Implemented', 'info')