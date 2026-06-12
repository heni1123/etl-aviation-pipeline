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
        row['icao24'] = self._br1_icao24(row)
        row['callsign'] = self._br2_callsign(row)
        row['origin_country'] = self._br3_origin_country(row)
        row['time_position'] = self._br4_time_position(row)
        row['last_contact'] = self._br5_last_contact(row)

    def _br1_icao24(self, row: Dict[str, Any]) -> str:
        return row['icao24']

    def _br2_callsign(self, row: Dict[str, Any]) -> str:
        return row['callsign']

    def _br3_origin_country(self, row: Dict[str, Any]) -> str:
        return row['origin_country']

    def _br4_time_position(self, row: Dict[str, Any]) -> int:
        return row['time_position']

    def _br5_last_contact(self, row: Dict[str, Any]) -> int:
        return row['last_contact']

    def _apply_derivations(self, row: Dict[str, Any], rates: Dict[str, Any]):
        pass  # No derived columns to apply

    def safe_div(self, a: float, b: float) -> float:
        return round(a / b, 8) if a and b and b != 0 else None