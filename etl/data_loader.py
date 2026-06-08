import asyncio
import logging
from typing import List, Dict, Any
from db_connection import get_connection_pool

class DataLoader:
    def __init__(self):
        self.pool = get_connection_pool()
        self.logger = self.setup_logger()

    def setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("DataLoader")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    async def load_data(self, enriched_List[Dict[str, Any]]) -> None:
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await self.truncate_table(connection)
                await self.insert_data(connection, enriched_data)

    async def truncate_table(self, connection) -> None:
        try:
            await connection.execute("TRUNCATE TABLE analytics.flight_operations_enriched")
            self.logger.info("Table analytics.flight_operations_enriched truncated successfully.")
        except Exception as e:
            self.logger.error(f"Error truncating table: {e}")
            raise

    async def insert_data(self, connection, enriched_List[Dict[str, Any]]) -> None:
        insert_query = """
        INSERT INTO analytics.flight_operations_enriched (
            icao24, callsign_clean, baro_altitude, altitude_ft, velocity, velocity_kmh,
            true_track, flight_direction, on_ground, is_in_flight, population_density,
            dep_country, arr_country, route_distance_km, is_international, last_contact_ts,
            loaded_at, emergency_flag, data_quality_flag, altitude_category, speed_category
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
        ON CONFLICT (icao24) DO UPDATE SET
            callsign_clean = EXCLUDED.callsign_clean,
            baro_altitude = EXCLUDED.baro_altitude,
            altitude_ft = EXCLUDED.altitude_ft,
            velocity = EXCLUDED.velocity,
            velocity_kmh = EXCLUDED.velocity_kmh,
            true_track = EXCLUDED.true_track,
            flight_direction = EXCLUDED.flight_direction,
            on_ground = EXCLUDED.on_ground,
            is_in_flight = EXCLUDED.is_in_flight,
            population_density = EXCLUDED.population_density,
            dep_country = EXCLUDED.dep_country,
            arr_country = EXCLUDED.arr_country,
            route_distance_km = EXCLUDED.route_distance_km,
            is_international = EXCLUDED.is_international,
            last_contact_ts = EXCLUDED.last_contact_ts,
            loaded_at = EXCLUDED.loaded_at,
            emergency_flag = EXCLUDED.emergency_flag,
            data_quality_flag = EXCLUDED.data_quality_flag,
            altitude_category = EXCLUDED.altitude_category,
            speed_category = EXCLUDED.speed_category
        """
        for record in enriched_data:
            try:
                await connection.execute(insert_query, 
                    record.get('icao24'), 
                    record.get('callsign_clean'), 
                    record.get('baro_altitude'), 
                    record.get('altitude_ft'), 
                    record.get('velocity'), 
                    record.get('velocity_kmh'), 
                    record.get('true_track'), 
                    record.get('flight_direction'), 
                    record.get('on_ground'), 
                    record.get('is_in_flight'), 
                    record.get('population_density'), 
                    record.get('dep_country'), 
                    record.get('arr_country'), 
                    record.get('route_distance_km'), 
                    record.get('is_international'), 
                    record.get('last_contact_ts'), 
                    record.get('loaded_at'), 
                    record.get('emergency_flag'), 
                    record.get('data_quality_flag'), 
                    record.get('altitude_category'), 
                    record.get('speed_category')
                )
                self.logger.info(f"Inserted record for icao24: {record.get('icao24')}")
            except Exception as e:
                self.logger.error(f"Error inserting record for icao24 {record.get('icao24')}: {e}")
                raise

async def main(enriched_List[Dict[str, Any]]) -> None:
    loader = DataLoader()
    await loader.load_data(enriched_data)

# The main function would be called with the enriched data in the actual ETL pipeline execution.