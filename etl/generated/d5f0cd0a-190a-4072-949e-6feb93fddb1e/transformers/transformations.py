import logging
from typing import List, Dict, Any
import math

class DataTransformer:
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def transform_batch(self, records: List[Dict]) -> List[Dict]:
        transformed_records = []
        for record in records:
            try:
                transformed_record = self._apply_all(record)
                transformed_records.append(transformed_record)
            except ValueError as e:
                self.logger.error(f"ValueError for record {record}: {e}")
        return transformed_records

    def _altitude_ft(self, record: Dict) -> Any:
        try:
            return round(float(record.get('baro_altitude', 0) or 0) * 3.28084, 0) if record.get('baro_altitude') else None
        except Exception as e:
            raise ValueError(f"Error calculating altitude_ft: {e}")

    def _velocity_kmh(self, record: Dict) -> Any:
        try:
            return round(float(record.get('velocity', 0) or 0) * 3.6, 1) if record.get('velocity') else None
        except Exception as e:
            raise ValueError(f"Error calculating velocity_kmh: {e}")

    def _flight_direction(self, record: Dict) -> Any:
        try:
            true_track = float(record.get('true_track', 0) or 0)
            if true_track < 90:
                return 'NE'
            elif true_track < 180:
                return 'SE'
            elif true_track < 270:
                return 'SW'
            else:
                return 'NW'
        except Exception as e:
            raise ValueError(f"Error calculating flight_direction: {e}")

    def _callsign_clean(self, record: Dict) -> Any:
        try:
            return str(record.get('callsign', '')).strip().upper()
        except Exception as e:
            raise ValueError(f"Error cleaning callsign: {e}")

    def _is_in_flight(self, record: Dict) -> Any:
        try:
            on_ground = record.get('on_ground', True)
            baro_altitude = record.get('baro_altitude', 0)
            return True if not on_ground and baro_altitude and float(baro_altitude) > 0 else False
        except Exception as e:
            raise ValueError(f"Error determining is_in_flight: {e}")

    def _population_density(self, record: Dict) -> Any:
        try:
            pop = record.get('pop', 0)
            area = record.get('country_area', 1)
            return round(float(pop) / float(area), 2) if area else None
        except Exception as e:
            raise ValueError(f"Error calculating population_density: {e}")

    def _route_distance_km(self, record: Dict) -> Any:
        try:
            dep_lat = record.get('dep_lat')
            dep_lon = record.get('dep_lon')
            arr_lat = record.get('arr_lat')
            arr_lon = record.get('arr_lon')
            if dep_lat and arr_lat:
                return self.haversine(dep_lat, dep_lon, arr_lat, arr_lon)
            return None
        except Exception as e:
            raise ValueError(f"Error calculating route_distance_km: {e}")

    def _is_international(self, record: Dict) -> Any:
        try:
            dep_country = record.get('dep_country')
            arr_country = record.get('arr_country')
            return dep_country != arr_country
        except Exception as e:
            raise ValueError(f"Error determining is_international: {e}")

    def _last_contact_ts(self, record: Dict) -> Any:
        try:
            return record.get('last_contact_ts')
        except Exception as e:
            raise ValueError(f"Error retrieving last_contact_ts: {e}")

    def _loaded_at(self, record: Dict) -> Any:
        try:
            return record.get('loaded_at')
        except Exception as e:
            raise ValueError(f"Error retrieving loaded_at: {e}")

    def _apply_all(self, record: Dict) -> Dict:
        transformed_record = {
            'altitude_ft': self._altitude_ft(record),
            'velocity_kmh': self._velocity_kmh(record),
            'flight_direction': self._flight_direction(record),
            'callsign_clean': self._callsign_clean(record),
            'is_in_flight': self._is_in_flight(record),
            'population_density': self._population_density(record),
            'route_distance_km': self._route_distance_km(record),
            'is_international': self._is_international(record),
            'last_contact_ts': self._last_contact_ts(record),
            'loaded_at': self._loaded_at(record),
        }
        return transformed_record

    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0  # Earth radius in kilometers
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c