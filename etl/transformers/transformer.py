import logging
from typing import List, Dict, Any

class Transformer:
    """Auto-generated transformer — 5 business rules, 0 derived columns."""

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

    def _apply_business_rules(self, row: Dict[str, Any]):
        self._br1_icao24(row)
        self._br2_callsign(row)
        self._br3_origin_country(row)
        self._br4_time_position(row)
        self._br5_velocity(row)

    def _br1_icao24(self, row: Dict[str, Any]):
        if row['icao24'] is None:
            logging.info("BR1: icao24 is missing.")

    def _br2_callsign(self, row: Dict[str, Any]):
        if row['callsign']:
            row['callsign'] = row['callsign'].strip().upper()

    def _br3_origin_country(self, row: Dict[str, Any]):
        if row['origin_country'] is None:
            logging.info("BR3: origin_country is missing.")

    def _br4_time_position(self, row: Dict[str, Any]):
        if not isinstance(row['time_position'], int):
            logging.info("BR4: time_position is not a valid integer.")

    def _br5_velocity(self, row: Dict[str, Any]):
        if row['velocity'] is not None and row['velocity'] < 0:
            logging.info("BR5: velocity must be non-negative.")

    def _apply_derivations(self, row: Dict[str, Any], rates: Dict[str, Any]):
        pass  # No derived columns to apply

    def safe_div(self, a: float, b: float) -> float:
        return round(a / b, 8) if a and b and b != 0 else None