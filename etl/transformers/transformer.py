class Transformer:
    """Auto-generated transformer — 4 business rules, 0 derived columns."""

    def transform(self, records: list, rates: dict = None) -> list:
        out = []
        for row in records:
            try:
                row = dict(row)
                self._apply_derivations(row)
                self._apply_business_rules(row)
                out.append(row)
            except Exception as e:
                import logging
                logging.warning(f"Transform error on {row.get('icao24')}: {e}")
        return out

    def _apply_derivations(self, row: dict):
        pass  # No derived columns defined

    def _apply_business_rules(self, row: dict):
        row['altitude_category'] = self._br1_altitude_category(row)
        row['speed_category'] = self._br3_speed_category(row)
        row['emergency_flag'] = self._br4_emergency_flag(row)
        row['data_quality_flag'] = self._br5_data_quality_flag(row)

    def _br1_altitude_category(self, row: dict) -> str:
        """BR1: Categorizes altitude based on barometric altitude"""
        if row.get('baro_altitude') is None or row.get('on_ground') is True:
            return 'Ground'
        elif 0 < row.get('baro_altitude') <= 3000:
            return 'Low Altitude'
        elif 3000 < row.get('baro_altitude') <= 7500:
            return 'Mid Altitude'
        elif 7500 < row.get('baro_altitude') <= 12500:
            return 'Cruise Altitude'
        elif row.get('baro_altitude') > 12500:
            return 'High Altitude'
        return None

    def _br3_speed_category(self, row: dict) -> str:
        """BR3: Categorizes speed based on velocity"""
        if row.get('velocity') is None or row.get('on_ground') == 'Unknown/Ground':
            return 'Unknown/Ground'
        elif 0 < row.get('velocity') <= 80:
            return 'Taxi/Slow'
        elif 80 < row.get('velocity') <= 150:
            return 'Approach'
        elif 150 < row.get('velocity') <= 230:
            return 'Climb/Descent'
        elif row.get('velocity') > 230:
            return 'Cruise'
        return None

    def _br4_emergency_flag(self, row: dict) -> str:
        """BR4: Flags emergency situations based on squawk code"""
        if row.get('squawk') == '7700':
            return 'General Emergency'
        elif row.get('squawk') == '7600':
            return 'Radio Failure'
        elif row.get('squawk') == '7500':
            return 'Hijacking'
        elif row.get('squawk') == '2000':
            return 'VFR No Transponder'
        elif row.get('spi') is True:
            return 'Special Purpose'
        elif row.get('squawk') is None or (row.get('squawk') != '7700' and row.get('spi') is not True):
            return 'Normal'
        return None

    def _br5_data_quality_flag(self, row: dict) -> str:
        """BR5: Assesses data quality based on various conditions"""
        if row.get('icao24') is None or row.get('callsign') is None:
            return 'Missing Required Fields'
        return 'Data Quality Good'