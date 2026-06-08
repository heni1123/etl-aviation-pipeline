import logging
from typing import List, Dict, Any

class DataValidator:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def validate_flight_data(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        validated_records = []
        for record in records:
            if self.is_valid_record(record):
                validated_records.append(record)
            else:
                self.logger.warning(f"Invalid record found: {record}")
        return validated_records

    def is_valid_record(self, record: Dict[str, Any]) -> bool:
        required_fields = ['icao24', 'callsign', 'baro_altitude', 'velocity', 'lat', 'lon']
        for field in required_fields:
            if record.get(field) is None:
                return False
        return True

    def validate_data_quality_flags(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for record in records:
            record['data_quality_flag'] = self.determine_data_quality_flag(record)
        return records

    def determine_data_quality_flag(self, record: Dict[str, Any]) -> str:
        if all(record.get(field) is not None for field in ['icao24', 'callsign', 'lat', 'lon']):
            return 'Complete'
        elif any(record.get(field) is not None for field in ['icao24', 'callsign']):
            return 'Partial'
        else:
            return 'Critical'

    def run_validation(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.info("Starting data validation process.")
        validated_records = self.validate_flight_data(records)
        validated_records = self.validate_data_quality_flags(validated_records)
        self.logger.info("Data validation process completed.")
        return validated_records