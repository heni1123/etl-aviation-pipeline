import os
import psycopg2
import psycopg2.extras
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlightOperationsLoader:
    def __init__(self) -> None:
        self.conn = psycopg2.connect(
            host=os.environ["DB_HOST"],
            port=os.environ.get("DB_PORT", "5432"),
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
        )
        self.conn.autocommit = False

    def load_data(self, rows: List[Dict[str, Any]]) -> None:
        try:
            with self.conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE analytics.flight_operations_enriched")
                psycopg2.extras.execute_batch(
                    cur,
                    "INSERT INTO analytics.flight_operations_enriched (icao24, callsign, origin_country, time_position, last_contact, longitude, latitude, baro_altitude, on_ground, velocity, true_track, vertical_rate, geo_altitude, squawk, spi, callsign_iata, airline_name, airline_iata, airline_icao, dep_airport_iata, dep_airport_icao, dep_airport_name, dep_city, dep_country, dep_latitude, dep_longitude, arr_airport_iata, arr_airport_icao, arr_airport_name, arr_city, arr_country, arr_latitude, arr_longitude, altitude_ft, velocity_kmh, flight_direction, population_density, callsign_clean, is_in_flight, route_distance_km, is_international, last_contact_ts, loaded_at) VALUES %s",
                    rows,
                    page_size=100,
                )
            self.conn.commit()
            logger.info(f"Successfully loaded {len(rows)} rows into analytics.flight_operations_enriched")
            self.write_audit_record(len(rows))
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error loading {e}")
            raise

    def write_audit_record(self, rows_loaded: int) -> None:
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO analytics.pipeline_runs (rows_loaded, run_time) VALUES (%s, NOW())",
                    (rows_loaded,)
                )
            self.conn.commit()
            logger.info("Audit record written successfully.")
        except Exception as e:
            logger.error(f"Error writing audit record: {e}")
            self.conn.rollback()
            raise

    def close(self) -> None:
        self.conn.close()