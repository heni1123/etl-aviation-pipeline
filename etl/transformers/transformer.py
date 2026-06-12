import logging
from typing import List, Dict, Any

class Transformer:
    """Auto-generated transformer — 4 business rules, 0 derived columns."""

    def transform(self, records: List[Dict[str, Any]], rates: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        out = []
        for row in records:
            try:
                row = dict(row)
                if rates:
                    row['_rates'] = rates
                self._apply_derivations(row, rates or {})
                self._apply_business_rules(row)
                out.append(row)
            except Exception as e:
                logging.warning(f"Transform error on {row.get('icao24')}: {e}")
        return out

    def _apply_derivations(self, row: Dict[str, Any], rates: Dict[str, Any]):
        pass  # No derivations to apply

    def _apply_business_rules(self, row: Dict[str, Any]):
        row['altitude_category'] = self._br1_altitude_category(row)
        row['speed_category'] = self._br3_speed_category(row)
        row['emergency_flag'] = self._br4_emergency_flag(row)
        row['data_quality_flag'] = self._br5_data_quality_flag(row)

    def _br1_altitude_category(self, row: Dict[str, Any]) -> str:
        baro_altitude = row.get('baro_altitude')
        on_ground = row.get('on_ground')
        if baro_altitude is None or on_ground:
            return 'Ground'
        elif 0 < baro_altitude <= 3000:
            return 'Low Altitude'
        elif 3000 < baro_altitude <= 7500:
            return 'Mid Altitude'
        elif 7500 < baro_altitude <= 12500:
            return 'Cruise Altitude'
        else:
            return 'High Altitude'

    def _br3_speed_category(self, row: Dict[str, Any]) -> str:
        velocity = row.get('velocity')
        on_ground = row.get('on_ground')
        if velocity is None or on_ground:
            return 'Unknown/Ground'
        elif 0 < velocity <= 80:
            return 'Taxi/Slow'
        elif 80 < velocity <= 150:
            return 'Approach'
        elif 150 < velocity <= 230:
            return 'Climb/Descent'
        else:
            return 'Cruise'

    def _br4_emergency_flag(self, row: Dict[str, Any]) -> str:
        squawk = row.get('squawk')
        spi = row.get('spi')
        if squawk == '7700':
            return 'General Emergency'
        elif squawk == '7600':
            return 'Radio Failure'
        elif squawk == '7500':
            return 'Hijacking'
        elif squawk == '2000':
            return 'VFR No Transponder'
        elif spi:
            return 'Special Purpose'
        else:
            return 'Normal'

    def _br5_data_quality_flag(self, row: Dict[str, Any]) -> str:
        if row.get('icao24') is None or row.get('callsign') is None:
            return 'Invalid'
        return 'Valid'