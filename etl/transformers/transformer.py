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
        self._br5_on_ground(row)

    def _br1_icao24(self, row: Dict[str, Any]):
        if row['icao24'] is None:
            logging.info("BR1: icao24 is not valid.")

    def _br2_callsign(self, row: Dict[str, Any]):
        if row.get('callsign'):
            row['callsign'] = row['callsign'].strip().upper()

    def _br3_origin_country(self, row: Dict[str, Any]):
        valid_iso_codes = ['US', 'FR', 'DE', 'GB']  # Example valid ISO codes
        if row['origin_country'] not in valid_iso_codes:
            logging.info("BR3: origin_country is not a valid ISO code.")

    def _br4_time_position(self, row: Dict[str, Any]):
        if row['time_position'] is None or row['time_position'] <= 0:
            logging.info("BR4: time_position is not a valid Unix timestamp.")

    def _br5_on_ground(self, row: Dict[str, Any]):
        if row['on_ground'] not in [True, False]:
            logging.info("BR5: on_ground must be either True or False.")