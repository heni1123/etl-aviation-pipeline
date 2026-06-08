import logging
from typing import List, Dict, Any
from haversine import haversine

class DataTransformer:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def transform(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed_records = []
        for row in records:
            try:
                transformed_row = {
                    "altitude_ft": self.calculate_altitude_ft(row),
                    "velocity_kmh": self.calculate_velocity_kmh(row),
                    "flight_direction": self.calculate_flight_direction(row),
                    "population_density": self.calculate_population_density(row),
                    "callsign_clean": self.clean_callsign(row),
                    "is_in_flight": self.check_in_flight(row),
                    "route_distance_km": self.calculate_route_distance_km(row),
                    "is_international": self.check_international(row),
                    "last_contact_ts": self.get_current_timestamp(),
                    "loaded_at": self.get_current_timestamp(),
                    "altitude_category": self.categorize_altitude(row),
                    "speed_category": self.categorize_speed(row),
                    "emergency_flag": self.flag_emergency(row),
                    "data_quality_flag": self.check_data_quality(row)
                }
                transformed_records.append(transformed_row)
            except Exception as e:
                self.logger.error(f"Error transforming record {row}: {e}")
        return transformed_records

    def calculate_altitude_ft(self, row: Dict[str, Any]) -> float:
        return round(float(row.get('baro_altitude', 0) or 0) * 3.28084, 0)

    def calculate_velocity_kmh(self, row: Dict[str, Any]) -> float:
        return round(float(row.get('velocity', 0) or 0) * 3.6, 1)

    def calculate_flight_direction(self, row: Dict[str, Any]) -> str:
        true_track = row.get('true_track', 0) or 0
        if true_track < 90:
            return 'NE'
        elif true_track < 180:
            return 'SE'
        elif true_track < 270:
            return 'SW'
        else:
            return 'NW'

    def calculate_population_density(self, row: Dict[str, Any]) -> float:
        population = float(row.get('population', 0))
        area = float(row.get('area', 1))
        return round(population / area, 2)

    def clean_callsign(self, row: Dict[str, Any]) -> str:
        return str(row.get('callsign', '')).strip().upper()

    def check_in_flight(self, row: Dict[str, Any]) -> bool:
        return row.get('on_ground') is False and float(row.get('baro_altitude', 0)) > 0

    def calculate_route_distance_km(self, row: Dict[str, Any]) -> float:
        dep_latitude = row.get('dep_latitude')
        dep_longitude = row.get('dep_longitude')
        arr_latitude = row.get('arr_latitude')
        arr_longitude = row.get('arr_longitude')
        if dep_latitude and arr_latitude:
            return haversine((dep_latitude, dep_longitude), (arr_latitude, arr_longitude))
        return None

    def check_international(self, row: Dict[str, Any]) -> bool:
        return row.get('dep_country') != row.get('arr_country')

    def get_current_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def categorize_altitude(self, row: Dict[str, Any]) -> str:
        baro_altitude = row.get('baro_altitude', 0)
        if baro_altitude is None:
            return 'Ground' if row.get('on_ground') else 'High Altitude'
        if baro_altitude <= 3000:
            return 'Low Altitude'
        elif baro_altitude <= 7500:
            return 'Mid Altitude'
        elif baro_altitude < 12500:
            return 'Cruise Altitude'
        else:
            return 'High Altitude'

    def categorize_speed(self, row: Dict[str, Any]) -> str:
        velocity = row.get('velocity', 0)
        if velocity is None:
            return 'Unknown/Ground'
        if velocity <= 80:
            return 'Taxi/Slow'
        elif velocity <= 150:
            return 'Approach'
        elif velocity <= 230:
            return 'Climb/Descent'
        else:
            return 'Cruise'

    def flag_emergency(self, row: Dict[str, Any]) -> str:
        squawk = row.get('squawk', 'Normal')
        if squawk == '7700':
            return 'General Emergency'
        elif squawk == '7600':
            return 'Radio Failure'
        elif squawk == '7500':
            return 'Hijacking'
        elif squawk == '2000':
            return 'VFR No Transponder'
        elif row.get('spi'):
            return 'Special Purpose'
        return 'Normal'

    def check_data_quality(self, row: Dict[str, Any]) -> str:
        if row.get('icao24') and row.get('callsign') and row.get('lat') is not None and row.get('lon') is not None and row.get('baro_altitude') is not None:
            return 'Complete'
        elif row.get('icao24') or row.get('callsign'):
            return 'Partial'
        return 'Critical'