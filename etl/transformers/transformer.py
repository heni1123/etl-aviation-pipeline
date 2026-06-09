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
                logging.warning(f"Transform error on {row.get('id')}: {e}")
        return out

    def _apply_derivations(self, row: Dict[str, Any], rates: Dict[str, Any]):
        pass  # No derivations to apply

    def _apply_business_rules(self, row: Dict[str, Any]):
        self._br1_icao24(row)
        self._br2_callsign(row)
        self._br3_origin_country(row)
        self._br4_time_position(row)
        self._br5_on_ground(row)

    def _br1_icao24(self, row: Dict[str, Any]):
        row['icao24'] = row.get('icao24')

    def _br2_callsign(self, row: Dict[str, Any]):
        row['callsign'] = row.get('callsign', '').strip().upper()

    def _br3_origin_country(self, row: Dict[str, Any]):
        row['origin_country'] = row.get('origin_country')

    def _br4_time_position(self, row: Dict[str, Any]):
        row['time_position'] = row.get('time_position')

    def _br5_on_ground(self, row: Dict[str, Any]):
        row['on_ground'] = row.get('on_ground')