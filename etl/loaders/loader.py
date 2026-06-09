import os
import psycopg2
import psycopg2.extras
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Loader:
    def load_data(self, rows: List[Dict[str, Any]]) -> None:
        try:
            conn = psycopg2.connect(
                host=os.environ["DB_HOST"],
                port=os.environ.get("DB_PORT", "5432"),
                dbname=os.environ["DB_NAME"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
            )
            conn.autocommit = False
            
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE analytics.cible")
                psycopg2.extras.execute_batch(
                    cur,
                    "INSERT INTO analytics.cible (icao24, callsign, origin_country, time_position, last_contact, longitude, latitude, baro_altitude, on_ground, velocity, true_track, vertical_rate, geo_altitude, squawk, spi, callsign_iata, airline_name, airline_iata, airline_icao, dep_airport_iata, dep_airport_icao, dep_airport_name, dep_city, dep_country, dep_latitude, dep_longitude, arr_airport_iata, arr_airport_icao, arr_airport_name, arr_city, arr_country, arr_latitude, arr_longitude, country_name, official_name, cca2, region, subregion, population, area, capital, continent) VALUES %s",
                    rows,
                    page_size=100,
                )
            conn.commit()
            logger.info(f"Rows loaded: {len(rows)}")
            self.audit_pipeline_run(len(rows))
        except Exception as e:
            conn.rollback()
            logger.error(f"Error loading {e}")
            raise
        finally:
            conn.close()

    def audit_pipeline_run(self, rows_loaded: int) -> None:
        try:
            conn = psycopg2.connect(
                host=os.environ["DB_HOST"],
                port=os.environ.get("DB_PORT", "5432"),
                dbname=os.environ["DB_NAME"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
            )
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO analytics.pipeline_runs (rows_loaded) VALUES (%s)",
                    (rows_loaded,)
                )
            conn.commit()
        except Exception as e:
            logger.error(f"Error auditing pipeline run: {e}")
            raise
        finally:
            conn.close()