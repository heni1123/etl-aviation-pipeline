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
        self._br4_on_ground(row)
        self._br5_velocity(row)

    def _br1_icao24(self, row: Dict[str, Any]):
        if row['icao24'] is None:
            logging.info("BR1: icao24 is not valid.")

    def _br2_callsign(self, row: Dict[str, Any]):
        if row['callsign']:
            row['callsign'] = row['callsign'].strip().upper()

    def _br3_origin_country(self, row: Dict[str, Any]):
        valid_iso_country_codes = self._fetch_valid_iso_country_codes()
        if row['origin_country'] not in valid_iso_country_codes:
            logging.info("BR3: origin_country is not a valid ISO country code.")

    def _br4_on_ground(self, row: Dict[str, Any]):
        if row['on_ground']:
            logging.info("BR4: Aircraft is marked as on ground.")

    def _br5_velocity(self, row: Dict[str, Any]):
        if not row['on_ground'] and (row['velocity'] <= 0):
            logging.info("BR5: Velocity must be greater than zero when the aircraft is in the air.")

    def _apply_derivations(self, row: Dict[str, Any], rates: Dict[str, Any]):
        pass  # No derived columns to implement

    def _fetch_valid_iso_country_codes(self) -> List[str]:
        # This method should implement the logic to fetch valid ISO country codes
        return []  # Placeholder for actual implementation